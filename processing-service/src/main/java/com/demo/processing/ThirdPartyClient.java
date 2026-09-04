package com.demo.processing;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.Duration;
import java.util.Map;
import java.util.UUID;

@Component
public class ThirdPartyClient {

    private final RestClient restClient;

    public ThirdPartyClient(@Value("${downstream.thirdparty-url}") String thirdpartyUrl) {
        var factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofSeconds(2));
        factory.setReadTimeout(Duration.ofSeconds(6));
        this.restClient = RestClient.builder()
                .baseUrl(thirdpartyUrl)
                .requestFactory(factory)
                .build();
    }

    public boolean enrich(UUID orderId, String scenario) {
        var request = restClient.post()
                .uri("/thirdparty/enrich")
                .contentType(MediaType.APPLICATION_JSON);
        if (scenario != null) {
            request = request.header("X-Scenario", scenario);
        }
        Map<String, Object> body = Map.of("orderId", orderId);
        Map<?, ?> result = request.body(body).retrieve().body(Map.class);
        return Boolean.TRUE.equals(result.get("enriched"));
    }
}
