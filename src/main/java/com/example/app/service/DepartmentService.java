package com.example.app.service;

import com.example.app.dto.DepartmentDto;
import com.example.app.dto.DepartmentRequest;
import com.example.app.entity.Department;
import com.example.app.entity.Department.DeptStatus;
import com.example.app.repository.DepartmentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DepartmentService {

    private final DepartmentRepository departmentRepository;

    public DepartmentDto create(DepartmentRequest request) {
        if (departmentRepository.existsByName(request.getName())) {
            throw new IllegalStateException("Department already exists: " + request.getName());
        }
        Department dept = new Department();
        dept.setName(request.getName());
        if (request.getStatus() != null && !request.getStatus().isBlank()) {
            try { dept.setStatus(DeptStatus.valueOf(request.getStatus().toUpperCase())); } catch (Exception ignored) {}
        }
        return mapToDto(departmentRepository.save(dept));
    }

    public List<DepartmentDto> getAll() {
        return departmentRepository.findAll().stream().map(this::mapToDto).collect(Collectors.toList());
    }

    public DepartmentDto getById(String id) {
        Department dept = departmentRepository.findById(UUID.fromString(id))
                .orElseThrow(() -> new RuntimeException("Department not found: " + id));
        return mapToDto(dept);
    }

    public DepartmentDto update(String id, DepartmentRequest request) {
        Department dept = departmentRepository.findById(UUID.fromString(id))
                .orElseThrow(() -> new RuntimeException("Department not found: " + id));
        dept.setName(request.getName());
        if (request.getStatus() != null && !request.getStatus().isBlank()) {
            try { dept.setStatus(DeptStatus.valueOf(request.getStatus().toUpperCase())); } catch (Exception ignored) {}
        }
        return mapToDto(departmentRepository.save(dept));
    }

    public void delete(String id) {
        Department dept = departmentRepository.findById(UUID.fromString(id))
                .orElseThrow(() -> new RuntimeException("Department not found: " + id));
        departmentRepository.delete(dept);
    }

    private DepartmentDto mapToDto(Department dept) {
        DepartmentDto dto = new DepartmentDto();
        dto.setId(dept.getId().toString());
        dto.setName(dept.getName());
        dto.setStatus(dept.getStatus().name());
        dto.setCreatedAt(dept.getCreatedAt());
        return dto;
    }
}
