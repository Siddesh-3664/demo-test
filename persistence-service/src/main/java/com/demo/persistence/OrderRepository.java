package com.demo.persistence;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

@Repository
public class OrderRepository {

    private final JdbcClient jdbcClient;

    public OrderRepository(JdbcClient jdbcClient) {
        this.jdbcClient = jdbcClient;
    }

    public void insert(PersistRequest r) {
        jdbcClient.sql("insert into orders(id,item,quantity,enriched) values(:id,:item,:quantity,:enriched)")
                .param("id", r.orderId())
                .param("item", r.item())
                .param("quantity", r.quantity())
                .param("enriched", r.enriched())
                .update();
    }
}
