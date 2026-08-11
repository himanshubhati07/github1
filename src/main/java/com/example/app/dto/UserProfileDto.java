package com.example.app.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class UserProfileDto {
    private String id;
    private String name;
    private String email;
    private String role;
    private String status;
    private LocalDateTime createdAt;
}
