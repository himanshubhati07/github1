package com.example.app.controller;

import com.example.app.dto.*;
import com.example.app.service.DashboardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/dashboard")
@Tag(name = "Dashboard", description = "Dashboard summary API")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping
    @Operation(summary = "Get today's attendance dashboard summary")
    public ResponseEntity<ApiResponse<DashboardDto>> getDashboard() {
        DashboardDto dto = dashboardService.getDashboard();
        return ResponseEntity.ok(ApiResponse.success(dto));
    }
}
