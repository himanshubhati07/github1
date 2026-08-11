package com.example.app.dto;

import lombok.Data;

@Data
public class TimeCardDto {
    private String employeeId;
    private String employeeName;
    private String department;
    private int totalWorkingDays;
    private int presentDays;
    private int absentDays;
    private int lateDays;
    private String totalWorkingHours;
    private String averageWorkingHours;
}
