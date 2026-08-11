package com.example.app.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;

@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    private boolean success;
    private String message;
    private String errorCode;
    private T data;

    public static <T> ApiResponse<T> success(String message, T data) {
        ApiResponse<T> r = new ApiResponse<>();
        r.success = true;
        r.message = message;
        r.data = data;
        return r;
    }

    public static <T> ApiResponse<T> success(T data) {
        return success("OK", data);
    }

    public static <T> ApiResponse<T> error(String message, String errorCode) {
        ApiResponse<T> r = new ApiResponse<>();
        r.success = false;
        r.message = message;
        r.errorCode = errorCode;
        return r;
    }
}
