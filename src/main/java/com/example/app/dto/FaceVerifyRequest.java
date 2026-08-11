package com.example.app.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class FaceVerifyRequest {

    @NotBlank(message = "Employee ID is required")
    private String employeeId;

    @NotBlank(message = "Face data/image is required")
    private String faceData;
}
