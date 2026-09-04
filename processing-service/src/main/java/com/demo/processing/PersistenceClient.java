package com.demo.processing;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.Duration;

@Component
public class PersistenceClient {

    private final RestClient restClient;

    public PersistenceClient(@Value("${downstream.persistence-url}") String persistenceUrl) {
        var factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofSeconds(2));
        factory.setReadTimeout(Duration.ofSeconds(6));
        this.restClient = RestClient.builder()
                .baseUrl(persistenceUrl)
                .requestFactory(factory)
                .build();
    }

    public void persist(ProcessResponse body, String scenario) {
        var request = restClient.post()
                .uri("/persist")
                .contentType(MediaType.APPLICATION_JSON);
        if (scenario != null) {
            request = request.header("X-Scenario", scenario);
        }
        request.body(body).retrieve().toBodilessEntity();
    }
}
