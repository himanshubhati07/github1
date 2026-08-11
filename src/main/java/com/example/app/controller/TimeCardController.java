package com.example.app.controller;

import com.example.app.dto.*;
import com.example.app.service.AttendanceService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/time-cards")
@Tag(name = "Time Cards", description = "Employee Time Card APIs")
@RequiredArgsConstructor
public class TimeCardController {

    private final AttendanceService attendanceService;

    @GetMapping("/{employeeId}")
    @Operation(summary = "Get time card for an employee by date range")
    public ResponseEntity<ApiResponse<TimeCardDto>> getTimeCard(
            @PathVariable String employeeId,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate) {
        TimeCardDto dto = attendanceService.getTimeCard(employeeId, startDate, endDate);
        return ResponseEntity.ok(ApiResponse.success(dto));
    }
}
