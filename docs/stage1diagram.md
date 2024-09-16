---
title: Stage 1 Architecture
---
%% this is a Mermaid chart, put this in https://mermaid.live to see it
sequenceDiagram
participant P as Pico
participant S as Server
participant G as Google Custom Search
participant V as Product Website
participant O as OpenAI
note right of P: WiFi
P->>S: UPC code
S->>G: UPC code
G->>S: Product Website URL
S->>V: Product Website URL
V->>S: Product page (HTML)
Note over S: Extract product data from HTML
S->>O: Product name, images, price, etc.
O->>S: Text description
Note over S: Local text-to-speech
note right of P: WiFi
S->>P: Voice description
