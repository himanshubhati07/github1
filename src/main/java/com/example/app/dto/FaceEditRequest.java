package com.example.app.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class FaceEditRequest {

    @NotBlank(message = "Face data/image is required")
    private String faceData;
}
