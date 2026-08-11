package com.example.app.service;

import com.example.app.dto.AttendanceDto;
import com.example.app.dto.TimeCardDto;
import com.example.app.entity.Attendance;
import com.example.app.entity.Attendance.AttendanceStatus;
import com.example.app.entity.Employee;
import com.example.app.repository.AttendanceRepository;
import com.example.app.repository.EmployeeRepository;
import lombok.RequiredArgsConstructor;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.StringWriter;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ReportService {

    private final AttendanceRepository attendanceRepository;
    private final EmployeeRepository employeeRepository;
    private final AttendanceService attendanceService;

    public List<AttendanceDto> getDailyAttendance(String dateStr, String department, String status) {
        LocalDate date = (dateStr != null && !dateStr.isBlank()) ? LocalDate.parse(dateStr) : LocalDate.now();
        AttendanceStatus attStatusTmp = null;
        if (status != null && !status.isBlank()) {
            try { attStatusTmp = AttendanceStatus.valueOf(status.toUpperCase()); } catch (Exception ignored) {}
        }
        final AttendanceStatus attStatus = attStatusTmp;
        final LocalDate finalDate = date;

        List<Attendance> records = attendanceRepository.findByAttendanceDate(finalDate);
        return records.stream()
                .filter(a -> {
                    if (attStatus != null && a.getStatus() != attStatus) return false;
                    if (department != null && !department.isBlank()) {
                        Employee emp = employeeRepository.findByEmployeeId(a.getEmployeeId()).orElse(null);
                        return emp != null && department.equals(emp.getDepartment());
                    }
                    return true;
                })
                .map(a -> {
                    Employee emp = employeeRepository.findByEmployeeId(a.getEmployeeId()).orElse(null);
                    return attendanceService.mapToDto(a, emp);
                })
                .collect(Collectors.toList());
    }

    public Map<String, Object> getMonthlyAttendance(String month, String department, String employeeId) {
        // month format: YYYY-MM
        LocalDate startDate;
        LocalDate endDate;
        if (month != null && !month.isBlank()) {
            String[] parts = month.split("-");
            int year = Integer.parseInt(parts[0]);
            int mon = Integer.parseInt(parts[1]);
            startDate = LocalDate.of(year, mon, 1);
            endDate = startDate.withDayOfMonth(startDate.lengthOfMonth());
        } else {
            startDate = LocalDate.now().withDayOfMonth(1);
            endDate = LocalDate.now();
        }

        List<Employee> employees;
        if (employeeId != null && !employeeId.isBlank()) {
            employees = employeeRepository.findByEmployeeId(employeeId).map(List::of).orElse(List.of());
        } else if (department != null && !department.isBlank()) {
            employees = employeeRepository.findAll().stream()
                    .filter(e -> department.equals(e.getDepartment()))
                    .collect(Collectors.toList());
        } else {
            employees = employeeRepository.findAll();
        }

        List<Map<String, Object>> summary = new ArrayList<>();
        for (Employee emp : employees) {
            List<Attendance> records = attendanceRepository
                    .findByEmployeeIdAndAttendanceDateBetween(emp.getEmployeeId(), startDate, endDate);
            int present = (int) records.stream().filter(a -> a.getStatus() != AttendanceStatus.ABSENT).count();
            int late = (int) records.stream().filter(a -> a.getStatus() == AttendanceStatus.LATE).count();
            summary.add(Map.of(
                    "employeeId", emp.getEmployeeId(),
                    "employeeName", emp.getName(),
                    "department", emp.getDepartment() != null ? emp.getDepartment() : "",
                    "presentDays", present,
                    "lateDays", late,
                    "absentDays", countWeekdays(startDate, endDate) - present
            ));
        }
        return Map.of(
                "month", startDate.getYear() + "-" + String.format("%02d", startDate.getMonthValue()),
                "startDate", startDate.toString(),
                "endDate", endDate.toString(),
                "summary", summary
        );
    }

    public TimeCardDto getTimeCardReport(String empId, String startDate, String endDate) {
        return attendanceService.getTimeCard(empId, startDate, endDate);
    }

    public Map<String, Object> getDepartmentAttendance(String dateStr, String department) {
        LocalDate date = (dateStr != null && !dateStr.isBlank()) ? LocalDate.parse(dateStr) : LocalDate.now();
        List<Employee> employees = employeeRepository.findAll().stream()
                .filter(e -> department == null || department.isBlank() || department.equals(e.getDepartment()))
                .collect(Collectors.toList());

        Map<String, List<Employee>> byDept = employees.stream()
                .collect(Collectors.groupingBy(e -> e.getDepartment() != null ? e.getDepartment() : "Unassigned"));

        List<Map<String, Object>> result = new ArrayList<>();
        for (Map.Entry<String, List<Employee>> entry : byDept.entrySet()) {
            String dept = entry.getKey();
            List<Employee> emps = entry.getValue();
            int present = 0;
            for (Employee e : emps) {
                if (attendanceRepository.existsByEmployeeIdAndAttendanceDate(e.getEmployeeId(), date)) {
                    present++;
                }
            }
            result.add(Map.of(
                    "department", dept,
                    "totalEmployees", emps.size(),
                    "present", present,
                    "absent", emps.size() - present
            ));
        }
        return Map.of("date", date.toString(), "departments", result);
    }

    public String exportAttendanceCsv(String startDateStr, String endDateStr, String employeeId) {
        LocalDate startDate = (startDateStr != null && !startDateStr.isBlank()) ? LocalDate.parse(startDateStr) : LocalDate.now().withDayOfMonth(1);
        LocalDate endDate = (endDateStr != null && !endDateStr.isBlank()) ? LocalDate.parse(endDateStr) : LocalDate.now();

        List<Attendance> records;
        if (employeeId != null && !employeeId.isBlank()) {
            records = attendanceRepository.findByEmployeeIdAndAttendanceDateBetween(employeeId, startDate, endDate);
        } else {
            records = attendanceRepository.findAll().stream()
                    .filter(a -> !a.getAttendanceDate().isBefore(startDate) && !a.getAttendanceDate().isAfter(endDate))
                    .collect(Collectors.toList());
        }

        StringWriter sw = new StringWriter();
        try (CSVPrinter printer = new CSVPrinter(sw, CSVFormat.DEFAULT
                .withHeader("Employee ID", "Employee Name", "Date", "Time In", "Time Out", "Working Hours", "Status"))) {
            for (Attendance a : records) {
                Employee emp = employeeRepository.findByEmployeeId(a.getEmployeeId()).orElse(null);
                printer.printRecord(
                        a.getEmployeeId(),
                        emp != null ? emp.getName() : "Unknown",
                        a.getAttendanceDate(),
                        a.getTimeIn() != null ? a.getTimeIn().toString() : "",
                        a.getTimeOut() != null ? a.getTimeOut().toString() : "",
                        a.getWorkingHours() != null ? a.getWorkingHours() : "",
                        a.getStatus().name()
                );
            }
        } catch (IOException e) {
            throw new RuntimeException("Failed to generate CSV", e);
        }
        return sw.toString();
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
}
