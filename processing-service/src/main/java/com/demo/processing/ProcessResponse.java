package com.demo.processing;

import java.util.UUID;

public record ProcessResponse(UUID orderId, String item, int quantity, boolean enriched) {
}
