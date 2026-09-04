package com.demo.processing;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClientException;

import java.util.Map;

@RestController
public class ProcessController {

    private static final Logger log = LoggerFactory.getLogger(ProcessController.class);

    private final ThirdPartyClient thirdPartyClient;
    private final PersistenceClient persistenceClient;

    public ProcessController(ThirdPartyClient thirdPartyClient, PersistenceClient persistenceClient) {
        this.thirdPartyClient = thirdPartyClient;
        this.persistenceClient = persistenceClient;
    }

    @PostMapping("/process")
    public ResponseEntity<?> process(@RequestBody ProcessRequest req,
                                     @RequestHeader(value = "X-Scenario", required = false) String scenario) {
        boolean enriched;
        try {
            enriched = thirdPartyClient.enrich(req.orderId(), scenario);
        } catch (RestClientException e) {
            String reason = e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage();
            log.error("Third-party enrich failed for order {}: {}", req.orderId(), reason);
            return ResponseEntity.status(502).body(Map.of("error", "third-party enrich failed: " + reason));
        }
        ProcessResponse resp = new ProcessResponse(req.orderId(), req.item(), req.quantity(), enriched);
        persistenceClient.persist(resp, scenario);
        return ResponseEntity.ok(resp);
    }
}
