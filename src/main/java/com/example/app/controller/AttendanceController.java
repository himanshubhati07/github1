package com.example.app.controller;

import com.example.app.dto.*;
import com.example.app.service.AttendanceService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/attendance")
@Tag(name = "Attendance", description = "Check-In, Check-Out, and Attendance History APIs")
@RequiredArgsConstructor
public class AttendanceController {

    private final AttendanceService attendanceService;

    @PostMapping("/check-in")
    @Operation(summary = "Employee check-in (time in)")
    public ResponseEntity<ApiResponse<AttendanceDto>> checkIn(@Valid @RequestBody CheckInRequest request) {
        AttendanceDto dto = attendanceService.checkIn(request);
        return ResponseEntity.status(201).body(ApiResponse.success("Checked in successfully", dto));
    }

    @PostMapping("/check-out")
    @Operation(summary = "Employee check-out (time out)")
    public ResponseEntity<ApiResponse<AttendanceDto>> checkOut(@Valid @RequestBody CheckOutRequest request) {
        AttendanceDto dto = attendanceService.checkOut(request);
        return ResponseEntity.ok(ApiResponse.success("Checked out successfully", dto));
    }

    @GetMapping
    @Operation(summary = "Get attendance history with filters and pagination")
    public ResponseEntity<ApiResponse<PagedResponse<AttendanceDto>>> getAttendance(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String sort,
            @RequestParam(required = false) String employeeId,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String search) {
        PagedResponse<AttendanceDto> result = attendanceService.getAttendance(
                page, size, sort, employeeId, startDate, endDate, status, department, search);
        return ResponseEntity.ok(ApiResponse.success(result));
    }
}
