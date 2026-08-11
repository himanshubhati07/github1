package com.example.app.service;

import com.example.app.dto.DashboardDto;
import com.example.app.entity.Attendance.AttendanceStatus;
import com.example.app.entity.Employee.EmpStatus;
import com.example.app.repository.AttendanceRepository;
import com.example.app.repository.EmployeeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class DashboardService {

    private final EmployeeRepository employeeRepository;
    private final AttendanceRepository attendanceRepository;

    public DashboardDto getDashboard() {
        LocalDate today = LocalDate.now();
        long totalEmployees = employeeRepository.countByStatus(EmpStatus.ACTIVE);
        long presentToday = attendanceRepository.countByAttendanceDateAndStatus(today, AttendanceStatus.PRESENT)
                + attendanceRepository.countByAttendanceDateAndStatus(today, AttendanceStatus.LATE);
        long lateToday = attendanceRepository.countByAttendanceDateAndStatus(today, AttendanceStatus.LATE);
        long currentlyCheckedIn = attendanceRepository.countCheckedInOnDate(today);
        long absentToday = Math.max(0, totalEmployees - presentToday);

        DashboardDto dto = new DashboardDto();
        dto.setTotalEmployees(totalEmployees);
        dto.setPresentToday(presentToday);
        dto.setAbsentToday(absentToday);
        dto.setCurrentlyCheckedIn(currentlyCheckedIn);
        dto.setLateToday(lateToday);
        dto.setTodaySummary(String.format("%d present, %d absent, %d late as of %s",
                presentToday, absentToday, lateToday, today));
        return dto;
    }
}
