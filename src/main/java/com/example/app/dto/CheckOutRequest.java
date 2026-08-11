package com.example.app.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CheckOutRequest {

    @NotBlank(message = "Employee ID is required")
    private String employeeId;
}
