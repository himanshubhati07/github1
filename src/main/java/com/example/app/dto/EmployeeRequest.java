package com.example.app.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import java.time.LocalDate;

@Data
public class EmployeeRequest {

    @NotBlank(message = "Employee ID is required")
    private String employeeId;

    @NotBlank(message = "Name is required")
    private String name;

    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    private String email;

    private String phone;
    private String department;
    private String designation;
    private LocalDate joiningDate;
    private String photo;
    private String status;
}
