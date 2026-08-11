package com.example.app.dto;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class AttendanceDto {
    private String id;
    private String employeeId;
    private String employeeName;
    private String department;
    private LocalDate attendanceDate;
    private String timeIn;
    private String timeOut;
    private String workingHours;
    private String status;
    private LocalDateTime createdAt;
}
