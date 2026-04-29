# Transformer Service

A **stateless, deterministic, and safe JSON-to-JSON transformation engine** built with FastAPI.

This service is part of **Delivero**, a webhook-based Event Delivery Platform, where it acts as the **transformation layer** between internal events and external subscriber systems.

---

## 🚀 Overview

The Transformer Service converts raw event payloads into **tenant-specific delivery formats** using a **declarative rule-based DSL**.

It ensures:

- predictable transformations
- safe execution (no arbitrary code)
- partial success with error visibility

Each request is processed independently, making the service:

- **stateless**
- **deterministic**
- **safe**

---

## 🧠 Design Philosophy

> A **deterministic JSON → JSON transformation engine with controlled capabilities**

### Core Principles

- No arbitrary code execution
- No external dependencies
- Same input + rule → same output
- Fail softly (no crashes on bad data)
- Strictly scoped DSL (MVP-first)

---

## 🏗️ Role in Delivero

```text
Producer → Orchestrator → Transformer → Webhook Delivery
```

- Orchestrator sends:
  - raw event payload
  - transformation rule

- Transformer:
  - applies rule
  - validates output
  - returns transformed payload

- Orchestrator:
  - handles delivery & retries

---

## ⚙️ Features

- JSON → JSON transformation
- Declarative DSL (no code execution)
- Output schema validation
- Partial transformation with error collection
- Nested object construction
- Array mapping
- Data masking
- Type normalization

---

## 📦 API

### POST `/transform`

#### Request

```json
{
  "payload": { ... },
  "rule": {
    "validation_schema": { ... },
    "transform_template": { ... }
  }
}
```

#### Response

```json
{
  "transformed_payload": { ... },
  "errors": []
}
```

---

## ⚠️ Error Handling Strategy

The transformer follows a **non-fatal error model**.

### Key Behavior

- Never crashes on transformation errors
- Returns partial output
- Collects errors in response
- Always returns **200 OK** for valid requests

### When 4xx is returned

- invalid request format
- invalid rule structure

---

## 🧩 Rule Structure

Each rule has two parts:

```json
{
  "validation_schema": { ... },
  "transform_template": { ... }
}
```

---

## 📘 1. `validation_schema` (Output Contract)

Defines the **expected structure of the transformed payload**.

### Supported (MVP)

- `type`
- `required`
- `properties`
- `items`

### Used for

- validating final output
- ensuring required fields
- type checking

### Not used for

- mapping fields
- transformations
- defaults

---

## 🛠️ 2. `transform_template` (DSL)

Defines how to build the output from the input payload.

### Core Structure

```json
{
  "output": {
    "field_name": {
      "path": "...",
      "transform": "...",
      "default": "...",
      "mask": "...",
      "condition": { ... },
      "object": { ... },
      "map": { ... },
      "value": "..."
    }
  }
}
```

---

## 🔧 Supported Operations (MVP)

### 1. Path Extraction

```json
{ "path": "payload.customer.email" }
```

---

### 2. Default Values

```json
{ "path": "payload.currency", "default": "INR" }
```

---

### 3. Type Transformations

- `to_string`
- `to_number`
- `to_boolean`

---

### 4. String Transformations

- `lowercase`
- `uppercase`
- `trim`

---

### 5. Constant Value

```json
{ "value": "fixed_value" }
```

---

### 6. Nested Object

```json
{
  "object": {
    "email": { "path": "payload.customer.email" }
  }
}
```

---

### 7. Array Mapping

```json
{
  "path": "payload.items",
  "map": {
    "id": { "path": "id" }
  }
}
```

---

### 8. Masking

- `last4`
- `full_mask`

---

### 9. Condition

```json
{
  "condition": {
    "path": "payload.amount",
    "operator": "gt",
    "value": 1000
  }
}
```

---

## ❌ Out of Scope (MVP)

- arbitrary code execution
- external API calls
- database access
- complex expressions (AND / OR)
- loops beyond array mapping
- joins or aggregations
- custom user-defined functions

---

## 🔄 Processing Flow

```text
1. Receive payload + rule
2. Validate rule structure
3. Execute transform_template
4. Generate transformed payload
5. Validate output using validation_schema
6. Return result + errors
```

---

## 🧪 Example

### Input Payload

```json
{
  "order": {
    "id": "ORD-10001",
    "summary": {
      "total_amount": "1250.75",
      "currency": null,
      "coupon_code": null
    },
    "flags": {
      "expedited": 1,
      "gift": "false"
    },
    "customer": {
      "name": "  Jane Doe  ",
      "email": "JANE.DOE@EXAMPLE.COM",
      "phone": "9876543210",
      "newsletter_opt_in": "true",
      "addresses": [
        {
          "type": "home",
          "is_primary": true,
          "line1": "221B Baker Street",
          "city": "London",
          "country": "uk",
          "geo": {
            "lat": "51.5237",
            "lng": "-0.1585"
          }
        },
        {
          "type": "work",
          "is_primary": false,
          "line1": "10 Downing Street",
          "city": "London",
          "country": "uk",
          "geo": {
            "lat": 51.5034,
            "lng": -0.1276
          }
        }
      ]
    },
    "items": [
      {
        "sku": "SKU-1",
        "qty": "2",
        "unit_price": "499.99",
        "product": {
          "id": "P-100",
          "name": "Wireless Mouse",
          "category": "accessories"
        },
        "seller": {
          "id": "S-900",
          "name": "  ACME Retail  "
        },
        "attributes": [
          {
            "key": "color",
            "value": "Black"
          },
          {
            "key": "warranty",
            "value": "12 months"
          }
        ]
      },
      {
        "sku": "SKU-2",
        "qty": 1,
        "unit_price": 250,
        "product": {
          "id": "P-200",
          "name": "Mechanical Keyboard",
          "category": "accessories"
        },
        "seller": {
          "id": "S-901",
          "name": "KeyWorld"
        },
        "attributes": [
          {
            "key": "layout",
            "value": "US"
          },
          {
            "key": "backlit",
            "value": "true"
          }
        ]
      }
    ]
  },
  "metadata": {
    "event_id": "evt_123",
    "source": "orchestrator"
  }
}
```

### Transform Template

```json
{
  "output": {
    "source_system": {
      "value": "OMS"
    },
    "order_id": {
      "path": "payload.order.id",
      "transform": "to_string"
    },
    "amount": {
      "path": "payload.order.summary.total_amount",
      "transform": "to_number"
    },
    "currency": {
      "path": "payload.order.summary.currency",
      "default": "INR"
    },
    "coupon_code": {
      "path": "payload.order.summary.coupon_code",
      "default": "NONE",
      "transform": "uppercase"
    },
    "is_high_value": {
      "condition": {
        "path": "payload.order.summary.total_amount",
        "operator": "gt",
        "value": 1000
      }
    },
    "is_expedited": {
      "condition": {
        "path": "payload.order.flags.expedited",
        "operator": "eq",
        "value": 1
      }
    },
    "gift_wrap": {
      "path": "payload.order.flags.gift",
      "transform": "to_boolean"
    },
    "customer": {
      "object": {
        "name": {
          "path": "payload.order.customer.name",
          "transform": "trim"
        },
        "email": {
          "path": "payload.order.customer.email",
          "transform": "lowercase"
        },
        "phone_last4": {
          "path": "payload.order.customer.phone",
          "mask": "last4"
        },
        "newsletter_opt_in": {
          "path": "payload.order.customer.newsletter_opt_in",
          "transform": "to_boolean"
        },
        "shipping_addresses": {
          "path": "payload.order.customer.addresses",
          "map": {
            "address_type": {
              "path": "type",
              "transform": "uppercase"
            },
            "is_primary": {
              "path": "is_primary",
              "transform": "to_boolean"
            },
            "line1": {
              "path": "line1",
              "transform": "trim"
            },
            "city": {
              "path": "city"
            },
            "country": {
              "path": "country",
              "transform": "uppercase"
            },
            "geo": {
              "object": {
                "lat": {
                  "path": "geo.lat",
                  "transform": "to_number"
                },
                "lng": {
                  "path": "geo.lng",
                  "transform": "to_number"
                }
              }
            }
          }
        }
      }
    },
    "items": {
      "path": "payload.order.items",
      "map": {
        "sku": {
          "path": "sku",
          "transform": "to_string"
        },
        "qty": {
          "path": "qty",
          "transform": "to_number"
        },
        "qty_text": {
          "path": "qty",
          "transform": "to_string"
        },
        "unit_price": {
          "path": "unit_price",
          "transform": "to_number"
        },
        "product": {
          "object": {
            "id": {
              "path": "product.id"
            },
            "name": {
              "path": "product.name",
              "transform": "trim"
            },
            "category": {
              "path": "product.category",
              "transform": "uppercase"
            }
          }
        },
        "seller": {
          "object": {
            "id": {
              "path": "seller.id"
            },
            "name": {
              "path": "seller.name",
              "transform": "trim"
            }
          }
        },
        "attributes": {
          "path": "attributes",
          "map": {
            "key": {
              "path": "key",
              "transform": "uppercase"
            },
            "value": {
              "path": "value"
            }
          }
        }
      }
    }
  }
}
```

### Validation Schema

```json
{
  "type": "object",
  "required": [
    "source_system",
    "order_id",
    "amount",
    "currency",
    "coupon_code",
    "is_high_value",
    "is_expedited",
    "gift_wrap",
    "customer",
    "items"
  ],
  "properties": {
    "source_system": {
      "type": "string"
    },
    "order_id": {
      "type": "string"
    },
    "amount": {
      "type": "number"
    },
    "currency": {
      "type": "string"
    },
    "coupon_code": {
      "type": "string"
    },
    "is_high_value": {
      "type": "boolean"
    },
    "is_expedited": {
      "type": "boolean"
    },
    "gift_wrap": {
      "type": "boolean"
    },
    "customer": {
      "type": "object",
      "required": [
        "name",
        "email",
        "phone_last4",
        "newsletter_opt_in",
        "shipping_addresses"
      ],
      "properties": {
        "name": {
          "type": "string"
        },
        "email": {
          "type": "string"
        },
        "phone_last4": {
          "type": "string"
        },
        "newsletter_opt_in": {
          "type": "boolean"
        },
        "shipping_addresses": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "address_type",
              "is_primary",
              "line1",
              "city",
              "country",
              "geo"
            ],
            "properties": {
              "address_type": {
                "type": "string"
              },
              "is_primary": {
                "type": "boolean"
              },
              "line1": {
                "type": "string"
              },
              "city": {
                "type": "string"
              },
              "country": {
                "type": "string"
              },
              "geo": {
                "type": "object",
                "required": ["lat", "lng"],
                "properties": {
                  "lat": {
                    "type": "number"
                  },
                  "lng": {
                    "type": "number"
                  }
                }
              }
            }
          }
        }
      }
    },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "sku",
          "qty",
          "qty_text",
          "unit_price",
          "product",
          "seller",
          "attributes"
        ],
        "properties": {
          "sku": {
            "type": "string"
          },
          "qty": {
            "type": "number"
          },
          "qty_text": {
            "type": "string"
          },
          "unit_price": {
            "type": "number"
          },
          "product": {
            "type": "object",
            "required": ["id", "name", "category"],
            "properties": {
              "id": {
                "type": "string"
              },
              "name": {
                "type": "string"
              },
              "category": {
                "type": "string"
              }
            }
          },
          "seller": {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
              "id": {
                "type": "string"
              },
              "name": {
                "type": "string"
              }
            }
          },
          "attributes": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["key", "value"],
              "properties": {
                "key": {
                  "type": "string"
                },
                "value": {
                  "type": "string"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

### Output

```json
{
  "transformed_payload": {
    "source_system": "OMS",
    "order_id": "ORD-10001",
    "amount": 1250.75,
    "currency": "INR",
    "coupon_code": "NONE",
    "is_high_value": true,
    "is_expedited": true,
    "gift_wrap": false,
    "customer": {
      "name": "Jane Doe",
      "email": "jane.doe@example.com",
      "phone_last4": "******3210",
      "newsletter_opt_in": true,
      "shipping_addresses": [
        {
          "address_type": "HOME",
          "is_primary": true,
          "line1": "221B Baker Street",
          "city": "London",
          "country": "UK",
          "geo": {
            "lat": 51.5237,
            "lng": -0.1585
          }
        },
        {
          "address_type": "WORK",
          "is_primary": false,
          "line1": "10 Downing Street",
          "city": "London",
          "country": "UK",
          "geo": {
            "lat": 51.5034,
            "lng": -0.1276
          }
        }
      ]
    },
    "items": [
      {
        "sku": "SKU-1",
        "qty": 2,
        "qty_text": "2",
        "unit_price": 499.99,
        "product": {
          "id": "P-100",
          "name": "Wireless Mouse",
          "category": "ACCESSORIES"
        },
        "seller": {
          "id": "S-900",
          "name": "ACME Retail"
        },
        "attributes": [
          {
            "key": "COLOR",
            "value": "Black"
          },
          {
            "key": "WARRANTY",
            "value": "12 months"
          }
        ]
      },
      {
        "sku": "SKU-2",
        "qty": 1,
        "qty_text": "1",
        "unit_price": 250,
        "product": {
          "id": "P-200",
          "name": "Mechanical Keyboard",
          "category": "ACCESSORIES"
        },
        "seller": {
          "id": "S-901",
          "name": "KeyWorld"
        },
        "attributes": [
          {
            "key": "LAYOUT",
            "value": "US"
          },
          {
            "key": "BACKLIT",
            "value": "true"
          }
        ]
      }
    ]
  },
  "errors": []
}
```

---

## 🏗️ Project Structure

```text
app/
  main.py
  modules/
    transformer/
      dto.py
      router.py
      service.py
      schema.py
      error_collector.py
      engine/
        executor.py
        resolver.py
        transformers.py
        validators.py
```

---

## ▶️ Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 💡 Design Decisions

### Why DSL instead of code?

- safety
- predictability
- no code injection risk

---

### Why stateless?

- horizontal scalability
- no shared state
- easier retries

---

### Why partial failures?

- prevents data loss
- improves observability
- aligns with event-driven systems

---

## ⚠️ MVP Limitations

- no DB integration
- no rule versioning
- no external data enrichment
- limited transformation functions

---

## 🔮 Future Improvements

- advanced conditions (AND / OR)
- computed fields
- rule versioning
- caching compiled rules
- performance optimization
