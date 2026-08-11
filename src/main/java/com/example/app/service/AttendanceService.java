package com.example.app.service;

import com.example.app.dto.*;
import com.example.app.entity.Attendance;
import com.example.app.entity.Attendance.AttendanceStatus;
import com.example.app.entity.Employee;
import com.example.app.repository.AttendanceRepository;
import com.example.app.repository.EmployeeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AttendanceService {

    private final AttendanceRepository attendanceRepository;
    private final EmployeeRepository employeeRepository;

    @Value("${app.office.start-hour:9}")
    private int officeStartHour;

    @Value("${app.office.start-minute:0}")
    private int officeStartMinute;

    public AttendanceDto checkIn(CheckInRequest request) {
        Employee employee = employeeRepository.findByEmployeeId(request.getEmployeeId())
                .orElseThrow(() -> new RuntimeException("Employee not found: " + request.getEmployeeId()));

        if (employee.getStatus() == Employee.EmpStatus.INACTIVE) {
            throw new IllegalStateException("Inactive employees cannot record attendance");
        }

        LocalDate today = LocalDate.now();
        if (attendanceRepository.existsByEmployeeIdAndAttendanceDate(request.getEmployeeId(), today)) {
            throw new IllegalStateException("Employee has already checked in today");
        }

        LocalTime now = LocalTime.now();
        LocalTime officeStart = LocalTime.of(officeStartHour, officeStartMinute);
        AttendanceStatus status = now.isAfter(officeStart) ? AttendanceStatus.LATE : AttendanceStatus.PRESENT;

        Attendance attendance = new Attendance();
        attendance.setEmployeeId(request.getEmployeeId());
        attendance.setAttendanceDate(today);
        attendance.setTimeIn(now);
        attendance.setStatus(status);

        Attendance saved = attendanceRepository.save(attendance);
        return mapToDto(saved, employee);
    }

    public AttendanceDto checkOut(CheckOutRequest request) {
        LocalDate today = LocalDate.now();
        Attendance attendance = attendanceRepository
                .findByEmployeeIdAndAttendanceDate(request.getEmployeeId(), today)
                .orElseThrow(() -> new IllegalStateException("No check-in found for today. Check in first."));

        if (attendance.getTimeIn() == null) {
            throw new IllegalStateException("Check in first before checking out");
        }
        if (attendance.getTimeOut() != null) {
            throw new IllegalStateException("Employee has already checked out today");
        }

        LocalTime now = LocalTime.now();
        if (!now.isAfter(attendance.getTimeIn())) {
            throw new IllegalStateException("Check out time must be after check in time");
        }

        attendance.setTimeOut(now);
        // Calculate working hours
        long minutes = attendance.getTimeIn().until(now, java.time.temporal.ChronoUnit.MINUTES);
        attendance.setWorkingHours(minutes / 60.0);

        Employee employee = employeeRepository.findByEmployeeId(request.getEmployeeId())
                .orElseThrow(() -> new RuntimeException("Employee not found"));

        Attendance saved = attendanceRepository.save(attendance);
        return mapToDto(saved, employee);
    }

    public PagedResponse<AttendanceDto> getAttendance(int page, int size, String sort,
                                                       String employeeId, String startDateStr, String endDateStr,
                                                       String statusStr, String department, String search) {
        // For native query, use the actual column name (snake_case)
        String sortCol = "attendance_date";
        Sort sortObj = Sort.by(Sort.Direction.DESC, sortCol);
        Pageable pageable = PageRequest.of(page, size, sortObj);

        LocalDate startDate = (startDateStr != null && !startDateStr.isBlank()) ? LocalDate.parse(startDateStr) : null;
        LocalDate endDate = (endDateStr != null && !endDateStr.isBlank()) ? LocalDate.parse(endDateStr) : null;
        String statusNorm = (statusStr != null && !statusStr.isBlank()) ? statusStr.toUpperCase() : null;

        Page<Attendance> pageResult = attendanceRepository.filterAttendance(
                (employeeId != null && employeeId.isBlank()) ? null : employeeId,
                startDate, endDate, statusNorm,
                (department != null && department.isBlank()) ? null : department,
                (search != null && search.isBlank()) ? null : search,
                pageable);

        List<AttendanceDto> dtos = pageResult.getContent().stream().map(a -> {
            Employee emp = employeeRepository.findByEmployeeId(a.getEmployeeId()).orElse(null);
            return mapToDto(a, emp);
        }).collect(Collectors.toList());

        return new PagedResponse<>(dtos, page, size, pageResult.getTotalElements());
    }

    public TimeCardDto getTimeCard(String empId, String startDateStr, String endDateStr) {
        Employee employee = employeeRepository.findByEmployeeId(empId)
                .orElseThrow(() -> new RuntimeException("Employee not found: " + empId));

        LocalDate startDate = (startDateStr != null && !startDateStr.isBlank())
                ? LocalDate.parse(startDateStr)
                : LocalDate.now().withDayOfMonth(1);
        LocalDate endDate = (endDateStr != null && !endDateStr.isBlank())
                ? LocalDate.parse(endDateStr)
                : LocalDate.now();

        List<Attendance> records = attendanceRepository
                .findByEmployeeIdAndAttendanceDateBetween(empId, startDate, endDate);

        int presentDays = (int) records.stream().filter(a -> a.getStatus() == AttendanceStatus.PRESENT || a.getStatus() == AttendanceStatus.LATE).count();
        int lateDays = (int) records.stream().filter(a -> a.getStatus() == AttendanceStatus.LATE).count();

        // Total working days = weekdays in range
        int totalWorkingDays = countWeekdays(startDate, endDate);
        int absentDays = Math.max(0, totalWorkingDays - presentDays);

        double totalHours = records.stream()
                .filter(a -> a.getWorkingHours() != null)
                .mapToDouble(Attendance::getWorkingHours)
                .sum();

        double avgHours = presentDays > 0 ? totalHours / presentDays : 0;

        TimeCardDto dto = new TimeCardDto();
        dto.setEmployeeId(empId);
        dto.setEmployeeName(employee.getName());
        dto.setDepartment(employee.getDepartment());
        dto.setTotalWorkingDays(totalWorkingDays);
        dto.setPresentDays(presentDays);
        dto.setAbsentDays(absentDays);
        dto.setLateDays(lateDays);
        dto.setTotalWorkingHours(formatHours(totalHours));
        dto.setAverageWorkingHours(formatHours(avgHours));
        return dto;
    }

    private int countWeekdays(LocalDate start, LocalDate end) {
        int count = 0;
        LocalDate d = start;
        while (!d.isAfter(end)) {
            if (d.getDayOfWeek() != java.time.DayOfWeek.SATURDAY
                    && d.getDayOfWeek() != java.time.DayOfWeek.SUNDAY) {
                count++;
            }
            d = d.plusDays(1);
        }
        return count;
    }

    private String formatHours(double hours) {
        int h = (int) hours;
        int m = (int) Math.round((hours - h) * 60);
        return h + "h " + m + "m";
    }

    public AttendanceDto mapToDto(Attendance a, Employee emp) {
        DateTimeFormatter timeFmt = DateTimeFormatter.ofPattern("hh:mm a");
        AttendanceDto dto = new AttendanceDto();
        dto.setId(a.getId().toString());
        dto.setEmployeeId(a.getEmployeeId());
        dto.setEmployeeName(emp != null ? emp.getName() : "Unknown");
        dto.setDepartment(emp != null ? emp.getDepartment() : null);
        dto.setAttendanceDate(a.getAttendanceDate());
        dto.setTimeIn(a.getTimeIn() != null ? a.getTimeIn().format(timeFmt) : null);
        dto.setTimeOut(a.getTimeOut() != null ? a.getTimeOut().format(timeFmt) : null);
        dto.setWorkingHours(a.getWorkingHours() != null ? formatHours(a.getWorkingHours()) : null);
        dto.setStatus(a.getStatus().name());
        dto.setCreatedAt(a.getCreatedAt());
        return dto;
    }
}
