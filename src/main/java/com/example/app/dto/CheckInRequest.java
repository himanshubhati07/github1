package com.example.app.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CheckInRequest {

    @NotBlank(message = "Employee ID is required")
    private String employeeId;
}
