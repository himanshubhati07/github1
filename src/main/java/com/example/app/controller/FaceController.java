package com.example.app.controller;

import com.example.app.dto.*;
import com.example.app.service.FaceService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/face")
@Tag(name = "Face Recognition", description = "Face Registration and Verification APIs")
@RequiredArgsConstructor
public class FaceController {

    private final FaceService faceService;

    @PostMapping("/register")
    @Operation(summary = "Register employee face data (demo/mock mode)")
    public ResponseEntity<ApiResponse<Map<String, Object>>> register(@Valid @RequestBody FaceRegisterRequest request) {
        Map<String, Object> result = faceService.registerFace(request);
        return ResponseEntity.status(201).body(ApiResponse.success("Face registered successfully", result));
    }

    @PostMapping("/verify")
    @Operation(summary = "Verify employee face data (demo/mock mode)")
    public ResponseEntity<ApiResponse<FaceVerifyResponse>> verify(@Valid @RequestBody FaceVerifyRequest request) {
        FaceVerifyResponse result = faceService.verifyFace(request);
        return ResponseEntity.ok(ApiResponse.success(result));
    }

    @PutMapping("/{employeeId}")
    @Operation(summary = "Edit/update registered face data for an employee")
    public ResponseEntity<ApiResponse<Map<String, Object>>> editFace(
            @PathVariable String employeeId,
            @Valid @RequestBody FaceEditRequest request) {
        Map<String, Object> result = faceService.updateFace(employeeId, request);
        return ResponseEntity.ok(ApiResponse.success("Face updated successfully", result));
    }
}
