package com.demo.processing;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProcessController {

    private final PersistenceClient persistenceClient;

    public ProcessController(PersistenceClient persistenceClient) {
        this.persistenceClient = persistenceClient;
    }

    @PostMapping("/process")
    public ProcessResponse process(@RequestBody ProcessRequest req,
                                   @RequestHeader(value = "X-Scenario", required = false) String scenario) {
        ProcessResponse resp = new ProcessResponse(req.orderId(), req.item(), req.quantity(), true);
        persistenceClient.persist(resp, scenario);
        return resp;
    }
}
