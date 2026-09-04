package com.demo.order;

import io.opentelemetry.api.trace.Span;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClientException;

import java.util.UUID;

@CrossOrigin(origins = "http://localhost:5173")
@RestController
public class OrderController {

    private final ProcessingClient processingClient;

    public OrderController(ProcessingClient processingClient) {
        this.processingClient = processingClient;
    }

    @PostMapping("/orders")
    public ResponseEntity<OrderResponse> orders(@Valid @RequestBody OrderRequest req,
                                                @RequestHeader(value = "X-Scenario", required = false) String scenario) {
        UUID orderId = UUID.randomUUID();
        String traceId = Span.current().getSpanContext().getTraceId();
        try {
            processingClient.process(orderId, req, scenario);
            OrderResponse body = new OrderResponse(orderId, traceId, "CREATED", null);
            return ResponseEntity.status(201)
                    .header("X-Trace-Id", traceId)
                    .body(body);
        } catch (RestClientException e) {
            String error = e.getMessage();
            if (error != null && error.length() > 200) {
                error = error.substring(0, 200);
            }
            OrderResponse body = new OrderResponse(orderId, traceId, "FAILED", error);
            return ResponseEntity.status(502)
                    .header("X-Trace-Id", traceId)
                    .body(body);
        }
    }
}
