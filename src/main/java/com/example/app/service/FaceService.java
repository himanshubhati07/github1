package com.example.app.service;

import com.example.app.dto.FaceRegisterRequest;
import com.example.app.dto.FaceVerifyRequest;
import com.example.app.dto.FaceVerifyResponse;
import com.example.app.entity.Employee;
import com.example.app.entity.FaceRegistration;
import com.example.app.repository.EmployeeRepository;
import com.example.app.repository.FaceRegistrationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class FaceService {

    private final EmployeeRepository employeeRepository;
    private final FaceRegistrationRepository faceRegistrationRepository;

    public Map<String, Object> registerFace(FaceRegisterRequest request) {
        Employee employee = employeeRepository.findByEmployeeId(request.getEmployeeId())
                .orElseThrow(() -> new RuntimeException("Employee not found: " + request.getEmployeeId()));

        if (employee.getStatus() == Employee.EmpStatus.INACTIVE) {
            throw new IllegalStateException("Cannot register face for inactive employee");
        }

        if (faceRegistrationRepository.existsByEmployeeId(request.getEmployeeId())) {
            throw new IllegalStateException("Face already registered for employee: " + request.getEmployeeId());
        }

        FaceRegistration face = new FaceRegistration();
        face.setEmployeeId(request.getEmployeeId());
        // In demo mode: store a simple hash/reference of the face data
        face.setFaceReference(generateFaceReference(request.getFaceData()));

        FaceRegistration saved = faceRegistrationRepository.save(face);

        return Map.of(
                "success", true,
                "employeeId", request.getEmployeeId(),
                "employeeName", employee.getName(),
                "message", "Face registered successfully",
                "registeredAt", saved.getRegisteredAt().toString()
        );
    }

    public FaceVerifyResponse verifyFace(FaceVerifyRequest request) {
        Employee employee = employeeRepository.findByEmployeeId(request.getEmployeeId())
                .orElseThrow(() -> new RuntimeException("Employee not found: " + request.getEmployeeId()));

        if (employee.getStatus() == Employee.EmpStatus.INACTIVE) {
            return new FaceVerifyResponse(false, false, request.getEmployeeId(),
                    employee.getName(), "Employee is inactive");
        }

        FaceRegistration registration = faceRegistrationRepository.findByEmployeeId(request.getEmployeeId())
                .orElseThrow(() -> new RuntimeException("Face not registered for employee: " + request.getEmployeeId()));

        // Demo/mock verification: compare hashes
        boolean verified = registration.getFaceReference().equals(generateFaceReference(request.getFaceData()));

        return new FaceVerifyResponse(
                true,
                verified,
                request.getEmployeeId(),
                employee.getName(),
                verified ? "Face verified successfully" : "Face verification failed"
        );
    }

    /**
     * Demo face reference generator — in production, use a real face recognition library.
     * Simply returns a stable hash of the face data string.
     */
    private String generateFaceReference(String faceData) {
        return "FACE_" + Integer.toHexString(faceData.hashCode()).toUpperCase();
    }
}
