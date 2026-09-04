package com.demo.processing;

import java.util.UUID;

public record ProcessRequest(UUID orderId, String item, int quantity) {
}
