package com.demo.order;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Min;

public record OrderRequest(@NotBlank String item, @Min(1) int quantity) {
}
