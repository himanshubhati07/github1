package com.example.app.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "face_registrations",
       uniqueConstraints = @UniqueConstraint(columnNames = "employeeId"))
@EntityListeners(AuditingEntityListener.class)
@Getter @Setter @NoArgsConstructor
public class FaceRegistration {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true)
    private String employeeId;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String faceReference;

    @Column(nullable = false, updatable = false)
    private LocalDateTime registeredAt;

    @LastModifiedDate
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    public void prePersist() {
        registeredAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
}
