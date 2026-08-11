package com.example.app.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class FaceVerifyResponse {
    private boolean success;
    private boolean verified;
    private String employeeId;
    private String employeeName;
    private String message;
}
