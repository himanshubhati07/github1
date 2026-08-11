package com.example.app.controller;

import com.example.app.dto.*;
import com.example.app.service.DepartmentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/departments")
@Tag(name = "Departments", description = "Department Management APIs")
@RequiredArgsConstructor
public class DepartmentController {

    private final DepartmentService departmentService;

    @PostMapping
    @Operation(summary = "Create a new department")
    public ResponseEntity<ApiResponse<DepartmentDto>> create(@Valid @RequestBody DepartmentRequest request) {
        DepartmentDto dto = departmentService.create(request);
        return ResponseEntity.status(201).body(ApiResponse.success("Department created", dto));
    }

    @GetMapping
    @Operation(summary = "Get all departments")
    public ResponseEntity<ApiResponse<List<DepartmentDto>>> getAll() {
        return ResponseEntity.ok(ApiResponse.success(departmentService.getAll()));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get department by ID")
    public ResponseEntity<ApiResponse<DepartmentDto>> getById(@PathVariable String id) {
        return ResponseEntity.ok(ApiResponse.success(departmentService.getById(id)));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update department")
    public ResponseEntity<ApiResponse<DepartmentDto>> update(@PathVariable String id,
                                                              @Valid @RequestBody DepartmentRequest request) {
        return ResponseEntity.ok(ApiResponse.success("Department updated", departmentService.update(id, request)));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete department")
    public ResponseEntity<ApiResponse<Void>> delete(@PathVariable String id) {
        departmentService.delete(id);
        return ResponseEntity.ok(ApiResponse.success("Department deleted", null));
    }
}
