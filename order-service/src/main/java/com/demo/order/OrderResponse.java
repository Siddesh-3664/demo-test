package com.demo.order;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.UUID;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record OrderResponse(UUID orderId, String traceId, String status, String error) {
}
