package com.example.app.controller;

import com.example.app.dto.*;
import com.example.app.service.ReportService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/reports")
@Tag(name = "Reports", description = "Attendance and Time Card Report APIs")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @GetMapping("/daily-attendance")
    @Operation(summary = "Get daily attendance report")
    public ResponseEntity<ApiResponse<List<AttendanceDto>>> dailyAttendance(
            @RequestParam(required = false) String date,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String status) {
        List<AttendanceDto> result = reportService.getDailyAttendance(date, department, status);
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @GetMapping("/monthly-attendance")
    @Operation(summary = "Get monthly attendance report (format: YYYY-MM)")
    public ResponseEntity<ApiResponse<Map<String, Object>>> monthlyAttendance(
            @RequestParam(required = false) String month,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String employeeId) {
        Map<String, Object> result = reportService.getMonthlyAttendance(month, department, employeeId);
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @GetMapping("/time-card/{employeeId}")
    @Operation(summary = "Get time card report for an employee")
    public ResponseEntity<ApiResponse<TimeCardDto>> timeCardReport(
            @PathVariable String employeeId,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        TimeCardDto dto = reportService.getTimeCardReport(employeeId, startDate, endDate);
        return ResponseEntity.ok(ApiResponse.success(dto));
    }

    @GetMapping("/department-attendance")
    @Operation(summary = "Get department-wise attendance report")
    public ResponseEntity<ApiResponse<Map<String, Object>>> departmentAttendance(
            @RequestParam(required = false) String date,
            @RequestParam(required = false) String department) {
        Map<String, Object> result = reportService.getDepartmentAttendance(date, department);
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @GetMapping("/export/csv")
    @Operation(summary = "Export attendance data as CSV")
    public ResponseEntity<String> exportCsv(
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate,
            @RequestParam(required = false) String employeeId) {
        String csv = reportService.exportAttendanceCsv(startDate, endDate, employeeId);
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=attendance.csv")
                .contentType(MediaType.parseMediaType("text/csv"))
                .body(csv);
    }
}
