package com.example.app.service;

import com.example.app.dto.EmployeeDto;
import com.example.app.dto.EmployeeRequest;
import com.example.app.dto.PagedResponse;
import com.example.app.entity.Employee;
import com.example.app.entity.Employee.EmpStatus;
import com.example.app.repository.EmployeeRepository;
import com.example.app.repository.FaceRegistrationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class EmployeeService {

    private final EmployeeRepository employeeRepository;
    private final FaceRegistrationRepository faceRegistrationRepository;

    public EmployeeDto create(EmployeeRequest request) {
        if (employeeRepository.existsByEmployeeId(request.getEmployeeId())) {
            throw new IllegalStateException("Employee ID already exists");
        }
        if (employeeRepository.existsByEmail(request.getEmail())) {
            throw new IllegalStateException("Employee email already exists");
        }

        Employee emp = new Employee();
        mapRequestToEntity(request, emp);
        Employee saved = employeeRepository.save(emp);
        return mapToDto(saved);
    }

    public PagedResponse<EmployeeDto> getAll(int page, int size, String sort, String search,
                                              String department, String status) {
        // For native query: use snake_case column names
        String sortCol = "name";
        Sort sortObj = Sort.by(Sort.Direction.ASC, sortCol);
        Pageable pageable = PageRequest.of(page, size, sortObj);
        String empStatusStr = (status != null && !status.isBlank()) ? status.toUpperCase() : null;
        Page<Employee> pageResult = employeeRepository.searchEmployees(
                (search != null && search.isBlank()) ? null : search,
                (department != null && department.isBlank()) ? null : department,
                empStatusStr, pageable);
        return new PagedResponse<>(pageResult.map(this::mapToDto).getContent(), page, size, pageResult.getTotalElements());
    }

    public EmployeeDto getById(String id) {
        Employee emp = findEmployee(id);
        return mapToDto(emp);
    }

    public EmployeeDto update(String id, EmployeeRequest request) {
        Employee emp = findEmployee(id);

        // Check uniqueness only if changed
        if (!emp.getEmployeeId().equals(request.getEmployeeId()) &&
                employeeRepository.existsByEmployeeId(request.getEmployeeId())) {
            throw new IllegalStateException("Employee ID already exists");
        }
        if (!emp.getEmail().equals(request.getEmail()) &&
                employeeRepository.existsByEmail(request.getEmail())) {
            throw new IllegalStateException("Employee email already exists");
        }

        mapRequestToEntity(request, emp);
        Employee saved = employeeRepository.save(emp);
        return mapToDto(saved);
    }

    public void deactivate(String id) {
        Employee emp = findEmployee(id);
        emp.setStatus(EmpStatus.INACTIVE);
        employeeRepository.save(emp);
    }

    public void delete(String id) {
        Employee emp = findEmployee(id);
        employeeRepository.delete(emp);
    }

    private Employee findEmployee(String id) {
        try {
            UUID uuid = UUID.fromString(id);
            return employeeRepository.findById(uuid)
                    .orElseThrow(() -> new RuntimeException("Employee not found: " + id));
        } catch (IllegalArgumentException e) {
            // Try by employeeId string
            return employeeRepository.findByEmployeeId(id)
                    .orElseThrow(() -> new RuntimeException("Employee not found: " + id));
        }
    }

    private void mapRequestToEntity(EmployeeRequest request, Employee emp) {
        emp.setEmployeeId(request.getEmployeeId());
        emp.setName(request.getName());
        emp.setEmail(request.getEmail());
        emp.setPhone(request.getPhone());
        emp.setDepartment(request.getDepartment());
        emp.setDesignation(request.getDesignation());
        emp.setJoiningDate(request.getJoiningDate());
        emp.setPhoto(request.getPhoto());
        if (request.getStatus() != null && !request.getStatus().isBlank()) {
            try { emp.setStatus(EmpStatus.valueOf(request.getStatus().toUpperCase())); }
            catch (Exception ignored) {}
        }
    }

    public EmployeeDto mapToDto(Employee emp) {
        EmployeeDto dto = new EmployeeDto();
        dto.setId(emp.getId().toString());
        dto.setEmployeeId(emp.getEmployeeId());
        dto.setName(emp.getName());
        dto.setEmail(emp.getEmail());
        dto.setPhone(emp.getPhone());
        dto.setDepartment(emp.getDepartment());
        dto.setDesignation(emp.getDesignation());
        dto.setJoiningDate(emp.getJoiningDate());
        dto.setPhoto(emp.getPhoto());
        dto.setStatus(emp.getStatus().name());
        dto.setFaceRegistered(faceRegistrationRepository.existsByEmployeeId(emp.getEmployeeId()));
        dto.setCreatedAt(emp.getCreatedAt());
        dto.setUpdatedAt(emp.getUpdatedAt());
        return dto;
    }
}
