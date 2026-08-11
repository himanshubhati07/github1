package com.example.app.controller;

import com.example.app.dto.*;
import com.example.app.service.EmployeeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/employees")
@Tag(name = "Employees", description = "Employee Management APIs")
@RequiredArgsConstructor
public class EmployeeController {

    private final EmployeeService employeeService;

    @PostMapping
    @Operation(summary = "Add a new employee")
    public ResponseEntity<ApiResponse<EmployeeDto>> create(@Valid @RequestBody EmployeeRequest request) {
        EmployeeDto dto = employeeService.create(request);
        return ResponseEntity.status(201).body(ApiResponse.success("Employee created successfully", dto));
    }

    @GetMapping
    @Operation(summary = "Get all employees with search, filter, and pagination")
    public ResponseEntity<ApiResponse<PagedResponse<EmployeeDto>>> getAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String sort,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String department,
            @RequestParam(required = false) String status) {
        PagedResponse<EmployeeDto> result = employeeService.getAll(page, size, sort, search, department, status);
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get employee by ID or employee code")
    public ResponseEntity<ApiResponse<EmployeeDto>> getById(@PathVariable String id) {
        EmployeeDto dto = employeeService.getById(id);
        return ResponseEntity.ok(ApiResponse.success(dto));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update employee details")
    public ResponseEntity<ApiResponse<EmployeeDto>> update(@PathVariable String id,
                                                            @Valid @RequestBody EmployeeRequest request) {
        EmployeeDto dto = employeeService.update(id, request);
        return ResponseEntity.ok(ApiResponse.success("Employee updated successfully", dto));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Deactivate (soft delete) employee")
    public ResponseEntity<ApiResponse<Void>> delete(@PathVariable String id) {
        employeeService.deactivate(id);
        return ResponseEntity.ok(ApiResponse.success("Employee deactivated successfully", null));
    }
}
