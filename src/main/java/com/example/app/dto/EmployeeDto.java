package com.example.app.dto;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class EmployeeDto {
    private String id;
    private String employeeId;
    private String name;
    private String email;
    private String phone;
    private String department;
    private String designation;
    private LocalDate joiningDate;
    private String photo;
    private String status;
    private boolean faceRegistered;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
