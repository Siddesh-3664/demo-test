package com.demo.order;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.Duration;
import java.util.UUID;

@Component
public class ProcessingClient {

    private final RestClient restClient;

    public ProcessingClient(@Value("${downstream.processing-url}") String processingUrl) {
        var factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofSeconds(2));
        factory.setReadTimeout(Duration.ofSeconds(10));
        this.restClient = RestClient.builder()
                .baseUrl(processingUrl)
                .requestFactory(factory)
                .build();
    }

    public void process(UUID orderId, OrderRequest req, String scenario) {
        var request = restClient.post()
                .uri("/process")
                .contentType(MediaType.APPLICATION_JSON);
        if (scenario != null) {
            request = request.header("X-Scenario", scenario);
        }
        var body = new ProcessRequest(orderId, req.item(), req.quantity());
        request.body(body).retrieve().toBodilessEntity();
    }

    private record ProcessRequest(UUID orderId, String item, int quantity) {
    }
}
