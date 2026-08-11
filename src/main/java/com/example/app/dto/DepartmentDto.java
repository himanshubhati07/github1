package com.example.app.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class DepartmentDto {
    private String id;
    private String name;
    private String status;
    private LocalDateTime createdAt;
}
