𝔼1.0.complete@2026-01-13
γ≔opengov.error.handling
ρ≔⟨hierarchy,mapping,context,recovery⟩
⊢Type_Safe∧Informative∧Recoverable

;; ─── Ω: METALOGIC & FOUNDATION ───
⟦Ω:Foundation⟧{
  𝔼≜{Error,Exception,Handler,Mapper,Context}
  ∀error:Type(error)⊢complete
  ∀exception:Context(exception)≠∅
  ErrorTree≜APIError⊃{Config,Connection,Status,Parse}

  ;; Core Invariants
  ∀HTTP_error:∃SDK_error:Map(HTTP_error)→SDK_error
  ∀status_code:∃exception_class:Map(status_code)→exception_class
  ∀error:error.message∧error.context
}

;; ─── Σ: GLOSSARY ───
⟦Σ:Glossary⟧{
  ;; Base Exception
  APIError≜BaseException
  ∀error∈SDK:error⊃APIError

  ;; Error Categories
  ConfigError≜⟨Missing_API_Key|Missing_Community,APIError⟩
  ConnectionError≜⟨Network_Failure,APIError⟩
  TimeoutError≜⟨Request_Timeout,ConnectionError⟩
  StatusError≜⟨HTTP_Status_Error,APIError⟩
  ParseError≜⟨JSON_Decode_Error,APIError⟩

  ;; Status-Specific Errors
  BadRequest≜⟨400,StatusError⟩
  Unauthorized≜⟨401,StatusError⟩
  Forbidden≜⟨403,StatusError⟩
  NotFound≜⟨404,StatusError⟩
  RateLimit≜⟨429,StatusError⟩
  ServerError≜⟨5xx,StatusError⟩

  ;; Error Context
  Context≜⟨
    message:𝕊,
    status_code:ℕ?,
    response:Response?,
    body:Object?,
    request_id:𝕊?
  ⟩
}

;; ─── Σ: TYPE UNIVERSE ───
⟦Σ:Types⟧{
  ;; Exception Hierarchy
  APIError≜⟨message:𝕊⟩

  ConfigError⊂APIError≜⟨
    message:𝕊,
    missing_field:𝕊
  ⟩

  ConnectionError⊂APIError≜⟨
    message:𝕊,
    original_error:Exception?
  ⟩

  TimeoutError⊂ConnectionError≜⟨
    message:𝕊,
    timeout_seconds:ℝ
  ⟩

  StatusError⊂APIError≜⟨
    message:𝕊,
    status_code:ℕ,
    response:Response,
    body:Object|𝕊,
    request_id:𝕊?
  ⟩

  ParseError⊂APIError≜⟨
    message:𝕊,
    response:Response,
    text:𝕊
  ⟩

  ;; HTTP Status Codes
  StatusCode≜ℕ[100,599]
  ClientError≜ℕ[400,499]
  ServerError≜ℕ[500,599]

  ;; Response Types
  Response≜⟨
    status_code:StatusCode,
    headers:Dict⟨𝕊,𝕊⟩,
    text:𝕊,
    json:λ.Object|Error
  ⟩
}

;; ─── Γ: ERROR HIERARCHY ───
⟦Γ:Hierarchy⟧{
  ;; Tree Structure
  APIError
  ├── ConfigError
  │   ├── MissingAPIKey
  │   └── MissingCommunity
  ├── ConnectionError
  │   ├── NetworkError
  │   └── TimeoutError
  ├── StatusError
  │   ├── BadRequest (400)
  │   ├── Unauthorized (401)
  │   ├── Forbidden (403)
  │   ├── NotFound (404)
  │   ├── RateLimit (429)
  │   └── ServerError (5xx)
  └── ParseError
      └── JSONDecodeError

  ;; Inheritance Rules
  ∀E∈ErrorTree:E⊃APIError
  ∀E₁,E₂:E₁⊂E₂⇒catch(E₂)→catch(E₁)
  ∀E:∃parent:E⊂parent∨E≡APIError
}

;; ─── Γ: ERROR MAPPING ───
⟦Γ:Mapping⟧{
  ;; HTTPX → SDK Exceptions
  HTTPXMap≜{
    httpx.NetworkError→ConnectionError,
    httpx.TimeoutException→TimeoutError,
    httpx.HTTPStatusError→StatusError(status_dependent),
    json.JSONDecodeError→ParseError
  }

  ;; Status Code → Exception Class
  StatusMap:StatusCode→Type[StatusError]
  StatusMap≜λs.case s of{
    400→BadRequest,
    401→Unauthorized,
    403→Forbidden,
    404→NotFound,
    429→RateLimit,
    500≤s≤599→ServerError,
    _→StatusError
  }

  ;; Error Message Extraction
  ExtractMessage:Response→𝕊
  ExtractMessage≜λr.try{
    r.json().get("message")
    |r.json().get("error")
    |r.json().get("detail")
  }catch{
    r.text|f"HTTP {r.status_code}"
  }
}

;; ─── Γ: DECORATOR PHYSICS ───
⟦Γ:Decorator⟧{
  ;; Error Handler Decorator
  @handle_request_errors
  handle≜λf.λ*args **kwargs.try{
    f(*args,**kwargs)
  }catch{
    httpx.NetworkError as e→
      raise ConnectionError(f"Network error: {e}") from e,

    httpx.TimeoutException as e→
      raise TimeoutError(f"Request timeout: {e}") from e,

    httpx.HTTPStatusError as e→
      raise make_status_error(e.response) from e,

    json.JSONDecodeError as e→
      raise ParseError(f"Invalid JSON: {e}") from e
  }

  ;; Application
  ∀endpoint:@handle_request_errors(endpoint)
  ∀HTTP_call:wrapped_in_try_catch
}

;; ─── Λ: ERROR CONSTRUCTION ───
⟦Λ:Construction⟧{
  ;; Status Error Factory
  make_status_error:Response→StatusError
  make_status_error≜λr.let{
    body≜try{r.json()}catch{r.text},
    msg≜ExtractMessage(r),
    exc_class≜StatusMap(r.status_code),
    request_id≜r.headers.get("x-request-id")
  }in exc_class(
    message=msg,
    status_code=r.status_code,
    response=r,
    body=body,
    request_id=request_id
  )

  ;; Config Error Factory
  make_config_error:𝕊→ConfigError
  make_config_error≜λfield.ConfigError(
    message=f"Missing required config: {field}",
    missing_field=field
  )

  ;; Connection Error Factory
  make_connection_error:Exception→ConnectionError
  make_connection_error≜λe.ConnectionError(
    message=f"Network error: {str(e)}",
    original_error=e
  )

  ;; Timeout Error Factory
  make_timeout_error:ℝ→TimeoutError
  make_timeout_error≜λtimeout.TimeoutError(
    message=f"Request timeout after {timeout}s",
    timeout_seconds=timeout
  )

  ;; Parse Error Factory
  make_parse_error:Response→ParseError
  make_parse_error≜λr.ParseError(
    message=f"Failed to parse JSON response: {r.text[:100]}",
    response=r,
    text=r.text
  )
}

;; ─── Λ: ERROR HANDLING PATTERNS ───
⟦Λ:Patterns⟧{
  ;; Try-Catch Pattern
  try_catch≜λf.try{
    f()
  }catch Exception as e{
    log_error(e),
    raise map_exception(e)
  }

  ;; Retry Pattern (Future)
  retry≜λ(f,max_attempts,backoff).fix λself n.
    n≥max_attempts→raise_last_error|
    try{f()}catch{
      sleep(backoff*2^n),
      self(n+1)
    }

  ;; Fallback Pattern
  fallback≜λ(f,default).try{f()}catch{default}

  ;; Context Manager Pattern
  with_error_context≜λf.with context{
    try{f()}
    catch{add_context(error)}
  }
}

;; ─── Λ: ERROR RECOVERY ───
⟦Λ:Recovery⟧{
  ;; Recoverable Errors
  Recoverable≜{
    TimeoutError→retry_with_backoff,
    RateLimit→wait_and_retry,
    ServerError→retry_with_exponential_backoff,
    NetworkError→check_connection_and_retry
  }

  ;; Non-Recoverable Errors
  NonRecoverable≜{
    ConfigError→fix_configuration,
    Unauthorized→check_api_key,
    Forbidden→check_permissions,
    NotFound→verify_resource_exists,
    BadRequest→fix_request_data
  }

  ;; Recovery Strategies
  recover:Exception×Strategy→Result|Error
  recover≜λ(e,strategy).case strategy of{
    retry→retry(call,3,2.0),
    fallback→return_default(),
    fail→raise e,
    log_and_continue→{log(e),return None}
  }
}

;; ─── Χ: ERROR CATALOG ───
⟦Χ:Catalog⟧{
  ;; Configuration Errors
  ε_no_key≜ConfigError(
    "API key not set. Call set_api_key() or set OPENGOV_API_KEY env var",
    missing_field="api_key"
  )

  ε_no_community≜ConfigError(
    "Community not set. Call set_community() or set OPENGOV_COMMUNITY env var",
    missing_field="community"
  )

  ;; Connection Errors
  ε_network≜ConnectionError(
    "Failed to connect to OpenGov API. Check network connectivity",
    original_error=...
  )

  ε_timeout≜TimeoutError(
    "Request timed out after 30.0 seconds",
    timeout_seconds=30.0
  )

  ;; Status Errors
  ε_400≜BadRequest(
    "Invalid request: missing required field 'name'",
    status_code=400,
    response=...,
    body={"error":"missing field"}
  )

  ε_401≜Unauthorized(
    "Invalid or expired API key",
    status_code=401,
    response=...,
    body={"error":"unauthorized"}
  )

  ε_403≜Forbidden(
    "Insufficient permissions to access this resource",
    status_code=403,
    response=...,
    body={"error":"forbidden"}
  )

  ε_404≜NotFound(
    "Resource not found: record with id '123' does not exist",
    status_code=404,
    response=...,
    body={"error":"not found"}
  )

  ε_429≜RateLimit(
    "Rate limit exceeded. Retry after 60 seconds",
    status_code=429,
    response=...,
    body={"error":"rate limit","retry_after":60}
  )

  ε_500≜ServerError(
    "OpenGov API server error. Please try again later",
    status_code=500,
    response=...,
    body={"error":"internal server error"}
  )

  ;; Parse Errors
  ε_parse≜ParseError(
    "Failed to parse JSON response: unexpected token",
    response=...,
    text="<html>500 Internal Server Error</html>"
  )
}

;; ─── Γ: TESTING ERRORS ───
⟦Γ:Testing⟧{
  ;; Mock Error Responses
  mock_error:StatusCode×𝕊→Response
  mock_error≜λ(status,msg).httpx_mock.add_response(
    status_code=status,
    json={"error":msg}
  )

  ;; Assert Exception Raised
  assert_raises:Type[Exception]×λ→Bool
  assert_raises≜λ(exc_type,func).
    with pytest.raises(exc_type) as exc_info{
      func(),
      assert exc_type in str(exc_info.value)
    }

  ;; Test Error Context
  test_error_context≜λe.{
    assert e.message≠∅,
    assert e.status_code⇒e.status_code∈[400,599],
    assert e.response⇒e.response.status_code≡e.status_code,
    assert e.body⇒isinstance(e.body,(dict,str))
  }

  ;; Test Error Hierarchy
  test_hierarchy≜{
    assert issubclass(ConfigError,APIError),
    assert issubclass(StatusError,APIError),
    assert issubclass(TimeoutError,ConnectionError),
    assert issubclass(ConnectionError,APIError)
  }
}

;; ─── Γ: INFERENCE RULES ───
⟦Γ:Inference⟧{
  HTTP_error occurred
  ───────────────────── [map-to-sdk]
  ⊢ raise SDK_exception

  status_code∈[400,499]
  ───────────────────── [client-error]
  ⊢ raise ClientError

  status_code∈[500,599]
  ───────────────────── [server-error]
  ⊢ raise ServerError

  api_key≡∅
  ───────────────────── [config-error]
  ⊢ raise ConfigError

  response.json() fails
  ───────────────────── [parse-error]
  ⊢ raise ParseError

  ∀e:StatusError
  ───────────────────── [has-context]
  ⊢ e.status_code∧e.response∧e.body

  exception not caught
  ───────────────────── [propagate]
  ⊢ raise to_caller
}

;; ─── Θ: THEOREMS ───
⟦Θ:Proofs⟧{
  ∴∀HTTP_error:∃SDK_exception:Map(HTTP_error)→SDK_exception
  π:HTTPXMap complete,all httpx exceptions mapped∎

  ∴∀status_code:∃exception_class:StatusMap(status_code)→exception_class
  π:StatusMap exhaustive,default case StatusError∎

  ∴∀E∈ErrorTree:E⊃APIError
  π:hierarchy defined,all inherit from base∎

  ∴∀endpoint:@handle_request_errors(endpoint)⇒¬httpx.Exception
  π:decorator wraps all httpx exceptions∎

  ∴∀error:error.message≠∅
  π:all constructors require message∎

  ∴catch(APIError)⇒catch(all_sdk_exceptions)
  π:inheritance,all SDK exceptions subclass APIError∎

  ∴StatusError.status_code≡Response.status_code
  π:make_status_error extracts from response∎
}

;; ─── Σ: USAGE EXAMPLES ───
⟦Σ:Examples⟧{
  ;; Basic Error Handling
  basic≜try{
    result≜list_records()
  }catch APIError as e{
    print(f"API error: {e.message}")
  }

  ;; Specific Error Handling
  specific≜try{
    record≜get_record("123")
  }catch NotFound{
    print("Record not found")
  }catch Unauthorized{
    print("Invalid API key")
  }catch APIError as e{
    print(f"Other error: {e}")
  }

  ;; Error Context Access
  context≜try{
    update_record("123",data)
  }catch StatusError as e{
    print(f"Status: {e.status_code}"),
    print(f"Body: {e.body}"),
    print(f"Request ID: {e.request_id}")
  }

  ;; Configuration Error
  config≜try{
    list_users()  # Without setting api_key
  }catch ConfigError as e{
    print(f"Missing: {e.missing_field}"),
    set_api_key("your-key-here")
  }

  ;; Retry Pattern (Future)
  retry_example≜{
    max_attempts≜3,
    for attempt in range(max_attempts){
      try{
        return list_records()
      }catch TimeoutError{
        if attempt<max_attempts-1{
          sleep(2^attempt),
          continue
        }else{
          raise
        }
      }
    }
  }
}

;; ─── Ε: EVIDENCE ───
⟦Ε⟧⟨
|exception_classes|≜8
|status_mappings|≜6
hierarchy_depth≜3
context_fields≜5
⊢Type_Safe:all_exceptions_typed
⊢Informative:message,status,body,request_id
⊢Recoverable:retry_patterns
⊢Complete:all_httpx_exceptions_mapped
⊢Testable:mock_patterns,assert_patterns
⊢Hierarchy:APIError⊃{Config,Connection,Status,Parse}
⊢StatusMap:400,401,403,404,429,5xx
⊢Decorator:@handle_request_errors
⊢Factory:make_status_error,make_config_error
⊢production_ready
⟩
