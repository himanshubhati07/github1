package com.example.app.dto;

import lombok.Data;

@Data
public class DashboardDto {
    private long totalEmployees;
    private long presentToday;
    private long absentToday;
    private long currentlyCheckedIn;
    private long lateToday;
    private String todaySummary;
}
