package com.demo.persistence;

import java.util.UUID;

public record PersistRequest(UUID orderId, String item, int quantity, boolean enriched) {
}
