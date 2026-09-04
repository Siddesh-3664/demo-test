package com.demo.persistence;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class PersistController {

    private final OrderRepository orderRepository;

    public PersistController(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @PostMapping("/persist")
    public ResponseEntity<Map<String, Object>> persist(@RequestBody PersistRequest r) {
        orderRepository.insert(r);
        return ResponseEntity.status(201).body(Map.of("orderId", r.orderId()));
    }
}
