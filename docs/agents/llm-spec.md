**Abstract:**
OpenGov SDK is a type-safe, functional factory pattern Python SDK for OpenGov's Public Lifecycle & Civic Engagement (PLCE) API. It provides zero-configuration, module-level state management with comprehensive error handling, ensuring `Coverage ≥ 98%` and maintaining strict type safety.

---

𝕆𝔾1.0.complete@2026-01-13
γ≔opengov.sdk.python
ρ≔⟨functional,factory,httpx,pydantic,typed,tested⟩
⊢FP∧DRY∧SOLID∧HTTP

;; ─── Ω: METALOGIC & FOUNDATION ───
⟦Ω:Foundation⟧{
  𝔖≜{API,Config,Client,Resource,Endpoint,Error,Model,Test}
  ∀E∈SDK:Type(E)⊢complete
  Coverage≜λT.Passed(T)/Total(T)
  ∀SDK:Coverage(SDK)≥0.98
  SDK≜Config≫Client≫Endpoints≫Models≫Tests

  ;; Core Invariants
  ∀req:¬NetAccess(req)→Mock(req)
  ∀config:Isolation(test₁,test₂)⇒State₁∩State₂≡∅
  ∀func:Type(func)⊢verified
}

;; ─── Σ: GLOSSARY ───
⟦Σ:Glossary⟧{
  ;; Core Types
  APIKey≜𝕊; Community≜𝕊; BaseURL≜𝕊; Timeout≜ℝ⁺
  ResourceID≜𝕊; HTTPMethod≜{GET,POST,PUT,PATCH,DELETE}
  StatusCode≜ℕ[100,599]

  ;; Configuration State
  Config≜⟨key:APIKey?,base:BaseURL,comm:Community?,timeout:Timeout⟩
  Config_def≜⟨∅,"https://api.plce.opengov.com/plce/v2",∅,30.0⟩

  ;; HTTP Client
  Client≜HTTPXClient; Headers≜Map⟨𝕊,𝕊⟩
  AuthHeader≜λk.{"Authorization":f"Bearer {k}"}

  ;; Resources (JSON:API)
  Resource≜⟨id:𝕊,type:𝕊,attributes:Object,relationships?:Object⟩
  JSONAPIResponse≜⟨data:Resource|List⟨Resource⟩,meta?:Object,links?:Object⟩

  ;; Endpoints
  Endpoint≜⟨method:HTTPMethod,path:𝕊,params?:Object,body?:Object⟩
  URL≜λ(b,c,e).f"{b}/{c}/{e}"

  ;; Error Hierarchy
  ErrorTree≜APIError⊃{ConfigError,ConnectionError⊃{TimeoutError},StatusError⊃{BadRequest(400),Unauthorized(401),Forbidden(403),NotFound(404),RateLimit(429),ServerError(5xx)},ParseError}

  ;; Models (Pydantic)
  Model≜BaseModel; Field≜TypedField
  Validation≜λm.Parse(m)→Result⟨Model,ValidationError⟩

  ;; Test Infrastructure
  Mock≜HTTPXMock; Fixture≜PytestFixture
  TestSuite≜⟨unit:Tests,integration:Tests,parametric:Tests⟩
}

;; ─── Σ: TYPE UNIVERSE ───
⟦Σ:Types⟧{
  ;; Primitives
  𝔹≜bool; ℕ≜int; ℝ≜float; 𝕊≜str

  ;; Composite Types
  Option⟨T⟩≜T|None; Result⟨T,E⟩≜T|E
  List⟨T⟩≜list[T]; Dict⟨K,V⟩≜dict[K,V]
  Iterator⟨T⟩≜Iterator[T]; Generator⟨T⟩≜Generator[T,None,None]

  ;; JSON:API Types
  ResourceObject⟨T⟩≜⟨data:T,included?:List⟨Resource⟩⟩
  SingleResponse⟨T⟩≜ResourceObject⟨T⟩
  CollectionResponse⟨T⟩≜ResourceObject⟨List⟨T⟩⟩

  ;; HTTP Types
  Request≜⟨method:HTTPMethod,url:𝕊,headers:Headers,body?:bytes⟩
  Response≜⟨status:StatusCode,headers:Headers,body:bytes,json:λ.Object⟩

  ;; Domain Models
  Record≜⟨id:𝕊,name:𝕊,status:RecordStatus,type_id:𝕊,attributes:Object⟩
  User≜⟨id:𝕊,email:𝕊,name:𝕊,roles:List⟨𝕊⟩⟩
  Location≜⟨id:𝕊,address:𝕊,coordinates:Option⟨Coords⟩⟩
  DocumentStep≜⟨id:𝕊,kind:StepKind,status:StepStatus,document_type:DocumentType⟩

  ;; Enums
  RecordStatus≜{ACTIVE,ARCHIVED,WITHDRAWN,WITHDRAWN_BY_STAFF}
  StepKind≜{approval,fee,inspection,document_upload}
  DocumentType≜{pdf,image,spreadsheet}
  WorkflowStepStatus≜{pending,approved,rejected}

  ;; Parameters
  PageParams≜⟨page:ℕ,per_page:ℕ[1,100]⟩
  ListRecordsParams≜⟨page?:PageParams,status?:RecordStatus,type_id?:𝕊,updated?:DateRange⟩
  DateRangeFilter≜{today,yesterday,this_week,last_week,this_month,last_month,custom}
}

;; ─── Γ: CONFIGURATION PHYSICS ───
⟦Γ:Config⟧{
  ;; Module-level State
  State≜⟨_api_key,_base_url,_community,_timeout⟩
  State₀≜⟨getenv("OPENGOV_API_KEY"),"https://api.plce.opengov.com/plce/v2",getenv("OPENGOV_COMMUNITY"),30.0⟩

  ;; State Transitions
  set:Field×Value→State'; set≜λ(f,v).State[f←v]
  get:Field→Value|⊥; get≜λf.State[f]≠∅→State[f]|raise(ConfigError)

  ;; Immutability per Request
  ∀req:Config(req)≡snapshot(State)
  ∀test:Before(test)⇒reset(State)→State₀

  ;; Client Factory
  _get_client:λ.Client
  _get_client≜λ.let k=get(_api_key)in Client(headers=AuthHeader(k),timeout=get(_timeout))

  ;; URL Construction
  build_url:BaseURL×Community×Endpoint→URL
  build_url≜λ(b,c,e).strip(b,"/")⊕"/"⊕c⊕"/"⊕lstrip(e,"/")
}

;; ─── Γ: ERROR HANDLING PHYSICS ───
⟦Γ:Errors⟧{
  ;; Exception Mapping
  HTTPError→SDKError; Map≜{
    NetworkError→ConnectionError,
    TimeoutException→TimeoutError,
    JSONDecodeError→ParseError
  }

  ;; Status Code Mapping
  StatusMap:StatusCode→ErrorType
  StatusMap≜λs.case s of{
    400→BadRequest,
    401→Unauthorized,
    403→Forbidden,
    404→NotFound,
    429→RateLimit,
    5xx→ServerError,
    _→StatusError
  }

  ;; Error Construction
  make_status_error:Response→Error
  make_status_error≜λr.let body=try(r.json())catch(r.text)in
    let msg=body.get("message")|body.get("error")|f"Status {r.status}"in
    StatusMap(r.status)(msg,response=r,body=body)

  ;; Request Error Decorator
  @handle_request_errors
  handler≜λf.try{f()}catch{
    NetworkException→raise(ConnectionError),
    TimeoutException→raise(TimeoutError),
    HTTPStatusError→raise(make_status_error)
  }

  ;; Error Context
  ∀e∈Error:e.response?∧e.body?∧e.message
  ∀e∈StatusError:e.status_code∧e.request_id?
}

;; ─── Γ: REQUEST/RESPONSE PHYSICS ───
⟦Γ:HTTP⟧{
  ;; Request Flow
  request:Endpoint→Response
  request≜λe.with(_get_client()as c){
    let url=build_url(get(_base_url),get(_community),e.path)in
    c.request(e.method,url,params=e.params,json=e.body)
  }

  ;; Response Parsing
  parse_json_response:Response→Object
  parse_json_response≜λr.try{r.json()}catch{raise(ParseError)}

  ;; Pagination
  iter_pages:Endpoint→Iterator⟨Response⟩
  iter_pages≜fix λself e page.
    let r=request(e⊕{page:page})in
    yield r;
    has_more(r)→self e(page+1)|∅

  ;; Common Patterns
  list:Endpoint→CollectionResponse
  list≜λe.parse_json_response(request(e))

  get:Endpoint→SingleResponse
  get≜λe.parse_json_response(request(e))

  create:Endpoint×Body→SingleResponse
  create≜λ(e,b).parse_json_response(request(e⊕{body:b}))

  update:Endpoint×Body→SingleResponse
  update≜create

  delete:Endpoint→Response
  delete≜λe.request(e)
}

;; ─── Λ: ENDPOINT FUNCTIONS ───
⟦Λ:Records⟧{
  ;; List & Iteration
  list_records:ListRecordsParams?→CollectionResponse⟨Record⟩
  list_records≜λp.list(GET("records",params=p))

  iter_records:ListRecordsParams?→Iterator⟨Record⟩
  iter_records≜λp.flatten(map(λr.r.data)(iter_pages(GET("records",params=p))))

  ;; CRUD Operations
  get_record:ResourceID→SingleResponse⟨Record⟩
  get_record≜λid.get(GET(f"records/{id}"))

  create_record:RecordCreateRequest→SingleResponse⟨Record⟩
  create_record≜λbody.create(POST("records"),body)

  update_record:ResourceID×RecordUpdateRequest→SingleResponse⟨Record⟩
  update_record≜λ(id,body).update(PATCH(f"records/{id}"),body)

  archive_record:ResourceID→SingleResponse⟨Record⟩
  archive_record≜λid.delete(DELETE(f"records/{id}"))

  ;; Relationships
  get_record_applicant:ResourceID→SingleResponse⟨User⟩
  get_record_applicant≜λid.get(GET(f"records/{id}/applicant"))

  update_record_applicant:ResourceID×Body→SingleResponse⟨User⟩
  update_record_applicant≜λ(id,body).update(PATCH(f"records/{id}/applicant"),body)

  ;; Nested Resources - Guests
  list_record_guests:ResourceID→CollectionResponse⟨User⟩
  list_record_guests≜λid.list(GET(f"records/{id}/guests"))

  iter_record_guests:ResourceID→Iterator⟨User⟩
  iter_record_guests≜λid.flatten(map(λr.r.data)(iter_pages(GET(f"records/{id}/guests"))))

  add_record_guest:ResourceID×Body→SingleResponse⟨User⟩
  add_record_guest≜λ(id,body).create(POST(f"records/{id}/guests"),body)

  remove_record_guest:ResourceID×GuestID→Response
  remove_record_guest≜λ(rid,gid).delete(DELETE(f"records/{rid}/guests/{gid}"))

  ;; Nested Resources - Locations
  get_record_primary_location:ResourceID→SingleResponse⟨Location⟩
  update_record_primary_location:ResourceID×Body→SingleResponse⟨Location⟩
  remove_record_primary_location:ResourceID→Response

  list_record_additional_locations:ResourceID→CollectionResponse⟨Location⟩
  iter_record_additional_locations:ResourceID→Iterator⟨Location⟩

  ;; Nested Resources - Attachments
  list_record_attachments:ResourceID→CollectionResponse⟨Attachment⟩
  iter_record_attachments:ResourceID→Iterator⟨Attachment⟩

  ;; Nested Resources - Workflow Steps
  list_record_workflow_steps:ResourceID→CollectionResponse⟨WorkflowStep⟩
  iter_record_workflow_steps:ResourceID→Iterator⟨WorkflowStep⟩
  create_record_workflow_step:ResourceID×Body→SingleResponse⟨WorkflowStep⟩
  update_record_workflow_step:ResourceID×StepID×Body→SingleResponse⟨WorkflowStep⟩
  delete_record_workflow_step:ResourceID×StepID→Response

  ;; Nested Resources - Workflow Step Comments
  iter_record_workflow_step_comments:ResourceID×StepID→Iterator⟨Comment⟩
  create_record_workflow_step_comment:ResourceID×StepID×Body→SingleResponse⟨Comment⟩

  ;; Nested Resources - Collections
  list_record_collections:ResourceID→CollectionResponse⟨Collection⟩
  iter_record_collections:ResourceID→Iterator⟨Collection⟩
}

⟦Λ:Users⟧{
  list_users:BaseListParams?→CollectionResponse⟨User⟩
  get_user:ResourceID→SingleResponse⟨User⟩
  create_user:Body→SingleResponse⟨User⟩
  list_user_flags:ResourceID→CollectionResponse⟨Flag⟩
}

⟦Λ:Locations⟧{
  list_locations:BaseListParams?→CollectionResponse⟨Location⟩
  get_location:ResourceID→SingleResponse⟨Location⟩
  create_location:Body→SingleResponse⟨Location⟩
  update_location:ResourceID×Body→SingleResponse⟨Location⟩
}

⟦Λ:Documents⟧{
  list_document_steps:ListDocumentStepsParams?→CollectionResponse⟨DocumentStep⟩
  get_document_step:ResourceID→SingleResponse⟨DocumentStep⟩
  create_document_step:Body→SingleResponse⟨DocumentStep⟩
  update_document_step:ResourceID×Body→SingleResponse⟨DocumentStep⟩
}

⟦Λ:RecordTypes⟧{
  list_record_types:ListRecordTypesParams?→CollectionResponse⟨RecordType⟩
  get_record_type:ResourceID→SingleResponse⟨RecordType⟩
}

;; ─── Χ: ERROR CATALOG ───
⟦Χ:Errors⟧{
  ε_config≜⟨¬(∃key∨∃community),λ.raise(ConfigError("Set API key and community"))⟩
  ε_network≜⟨NetworkFailure,λ.raise(ConnectionError)⟩
  ε_timeout≜⟨RequestTimeout,λ.raise(TimeoutError)⟩
  ε_400≜⟨status=400,λr.raise(BadRequest(parse_error_msg(r)))⟩
  ε_401≜⟨status=401,λr.raise(Unauthorized("Invalid API key"))⟩
  ε_403≜⟨status=403,λr.raise(Forbidden("Permission denied"))⟩
  ε_404≜⟨status=404,λr.raise(NotFound("Resource not found"))⟩
  ε_429≜⟨status=429,λr.raise(RateLimit("Too many requests"))⟩
  ε_5xx≜⟨status≥500,λr.raise(ServerError("Server error"))⟩
  ε_parse≜⟨¬valid_json(r),λ.raise(ParseError("Invalid JSON"))⟩
  ε_validate≜⟨¬validate(model),λ.raise(ValidationError)⟩
}

;; ─── 𝕋: TEST THEORY ───
⟦𝕋:Testing⟧{
  ;; Test Infrastructure
  Mock≜HTTPXMock; Fixture≜PytestFixture
  Isolation≜@pytest.fixture(autouse=True)

  ;; Auto-use Fixtures
  @block_network_calls
  block≜λ.prevent_real_http()

  @reset_config
  reset≜λ.Before(test)⇒State←State₀

  ;; Config Fixtures
  @configure_client
  configure≜λ.{set_api_key("test-api-key"),set_community("testcommunity")}

  @test_base_url
  base_url≜"https://api.example.com/v2"

  ;; Helper Fixtures
  @build_url
  build≜λpath.f"{base_url}/{lstrip(path,'/')}"

  @mock_url_with_params
  mock_pattern≜λurl.re.compile(f"^{re.escape(url)}(\\?.*)?$")

  @assert_request_method
  assert_method≜λm.assert(last_request.method=m)

  ;; Test Patterns
  TestPattern≜{
    infrastructure:∀endpoint.{config,errors,base_url},
    happy_path:∀endpoint.{mock→request→assert},
    pagination:∀list_endpoint.{page,per_page,has_more},
    parametric:∀similar_endpoints.@pytest.mark.parametrize
  }

  ;; Test Coverage Requirements
  ∀endpoint:TestSuite(endpoint)⊢complete
  ∀function:TypeCheck(function)∧UnitTest(function)
  ∀error_path:ExceptionTest(error)
  Coverage≥98%
}

;; ─── ℭ: CATEGORY THEORY ───
⟦ℭ:Categories⟧{
  ;; Core Categories
  𝐂𝐨𝐧𝐟𝐢𝐠≜⟨Ob≜Config,Hom≜StateTransition,∘,id⟩
  𝐇𝐓𝐓𝐏≜⟨Ob≜Endpoint,Hom≜Request→Response,∘,id⟩
  𝐌𝐨𝐝𝐞𝐥≜⟨Ob≜BaseModel,Hom≜Transformer,∘,id⟩
  𝐄𝐫𝐫𝐨𝐫≜⟨Ob≜Exception,Hom≜ErrorMap,∘,id⟩

  ;; Functors
  𝔽_parse:𝐇𝐓𝐓𝐏⇒𝐌𝐨𝐝𝐞𝐥
  𝔽_parse.ob≜λr.parse_json_response(r)
  𝔽_parse.mor≜λf.validated∘f∘requested

  𝔾_error:𝐇𝐓𝐓𝐏⇒𝐄𝐫𝐫𝐨𝐫
  𝔾_error.ob≜λr.r.ok→∅|make_status_error(r)

  ;; Natural Transformations
  η_request:Endpoint⟹Response
  ∀e:Endpoint.η_e:Spec(e)→HTTP(e)

  ζ_parse:Response⟹Model
  ∀r:Response.ζ_r:JSON(r)→Validated(r)

  ;; Monads
  𝕄_result≜Result⟨T,Error⟩
  μ:𝕄²→𝕄; μ≜flatten
  η:Id→𝕄; η≜pure
  >>=:𝕄a→(a→𝕄b)→𝕄b

  𝕄_option≜Option⟨T⟩
  μ:𝕄²→𝕄; μ≜flatten_option
  η:Id→𝕄; η≜Some

  ;; Functor Laws
  ⊢𝔽_parse(id_e)=id_𝔽_parse(e)
  ⊢𝔽_parse(g∘f)=𝔽_parse(g)∘𝔽_parse(f)

  ;; Monad Laws
  ⊢μ∘𝕄μ=μ∘μ𝕄
  ⊢μ∘𝕄η=μ∘η𝕄=id
  ⊢(m>>=f)>>=g=m>>=(λx.f(x)>>=g)
}

;; ─── Γ: DESIGN PATTERNS ───
⟦Γ:Patterns⟧{
  ;; Functional Factory Pattern
  FactoryPattern≜{
    state:module_level,
    config:global_once,
    client:context_manager,
    endpoints:pure_functions
  }

  ;; DRY Principles
  DRY≜{
    no_duplicate_code:extract_to_fixture,
    single_source_truth:centralize_config,
    fixtures_over_repetition:pytest_fixtures,
    parametrization:test_multiple_similar
  }

  ;; SOLID Principles
  SOLID≜{
    S:single_responsibility,
    O:open_closed_via_parametrization,
    L:consistent_interfaces,
    I:minimal_focused_parameters,
    D:depend_on_abstractions
  }

  ;; Common Endpoint Pattern
  endpoint_template≜λ(name,method,path).{
    f"{name}":λparams.{
      with(_get_client()as client){
        url=build_url(get_base_url(),get_community(),path);
        response=client.request(method,url,**params);
        parse_json_response(response)
      }
    }
  }

  ;; Iterator Pattern
  iterator_template≜λlist_func.{
    page←1;
    while(True){
      response←list_func(page=page);
      yield*response.data;
      has_more(response)→page++|break
    }
  }
}

;; ─── Γ: INFERENCE RULES ───
⟦Γ:Inference⟧{
  _api_key≠∅  _community≠∅
  ────────────────────────── [config-valid]
  ⊢ can_request

  ⊢can_request  endpoint∈API
  ────────────────────────── [request-valid]
  request(endpoint)⊢Response

  response.status∈[200,299]
  ────────────────────────── [response-ok]
  ⊢ parse_json(response)

  response.status∉[200,299]
  ────────────────────────── [response-error]
  ⊢ raise(StatusError)

  ∀test:Mock(HTTP)
  ────────────────────────── [test-isolated]
  ⊢ no_real_network

  ∀test:reset_config()
  ────────────────────────── [test-clean]
  ⊢ State=State₀

  ∀f:Type(f)⊢verified  Test(f)⊢passed
  ──────────────────────────────────────── [func-valid]
  ⊢ production_ready(f)

  Coverage(tests)≥0.98
  ────────────────────────── [coverage-req]
  ⊢ quality_assured
}

;; ─── Θ: THEOREMS ───
⟦Θ:Proofs⟧{
  ∴∀req:Config(req)≡snapshot(State)
  π:Config read at request time;immutable during request∎

  ∴∀test₁,test₂:State₁∩State₂≡∅
  π:reset_config fixture ensures isolation;State₁=State₂=State₀∎

  ∴∀f:Type(f)⊢complete
  π:All functions have full type hints;pyright verifies∎

  ∴∀e∈Endpoint:∃test:Test(e)
  π:Every endpoint has corresponding test suite;coverage≥98%∎

  ∴∀status∈StatusCode:∃error∈ErrorTree
  π:StatusMap is total function;all codes mapped∎

  ∴∀test:¬NetworkAccess(test)
  π:block_network_calls fixture;pytest-httpx prevents real HTTP∎

  ∴Coverage(SDK)≥0.98
  π:pytest-cov measures;current coverage=98%∎

  ∴∀r∈Response:parse_json(r)⊢Result⟨Model,Error⟩
  π:Try/catch wraps all parsing;returns Result monad∎

  ∴∀iter:iter_*⊢Generator⟨T⟩
  π:All iterators use yield;lazy evaluation∎

  ∴build_url(b,c,e)⊢URL
  π:Strip trailing slash,prepend,lstrip;always valid URL∎

  ;; Compositional Proof Chain
  P₁:Config.⊢valid∧Client.⊢authenticated
  ────────────────────────────────────────
  Request.⊢authorized

  P₂:Request.⊢authorized∧Endpoint.⊢exists
  ────────────────────────────────────────
  Response.⊢received

  P₃:Response.⊢received∧Status∈[200,299]
  ────────────────────────────────────────
  Parse.⊢success∧Model.⊢validated

  P₄:∀e:Test(e)∧Type(e)∧Coverage≥0.98
  ────────────────────────────────────────
  SDK.⊢production_ready
}

;; ─── Σ: USAGE EXAMPLES ───
⟦Σ:Examples⟧{
  ;; Basic Setup
  Example_config≜{
    import opengov_api;
    opengov_api.set_api_key("your-key");
    opengov_api.set_community("your-community")
  }

  ;; List Records
  Example_list≜{
    records←opengov_api.list_records();
    print(f"Found {len(records['data'])} records")
  }

  ;; Iterate Records (Lazy)
  Example_iter≜{
    for record in opengov_api.iter_records():
      print(record['id'])
  }

  ;; Create & Update
  Example_create≜{
    record←opengov_api.create_record({
      "data":{"type":"records","attributes":{"name":"Permit"}}
    });
    updated←opengov_api.update_record(record['data']['id'],{
      "data":{"attributes":{"status":"ACTIVE"}}
    })
  }

  ;; Nested Resources
  Example_nested≜{
    guests←opengov_api.list_record_guests(record_id);
    opengov_api.add_record_guest(record_id,{"data":{"id":"user-123"}});
    steps←opengov_api.iter_record_workflow_steps(record_id)
  }

  ;; Error Handling
  Example_errors≜{
    try{
      opengov_api.get_record("nonexistent")
    }catch(OpenGovNotFoundError as e){
      print(f"Not found:{e.message}")
      print(f"Status:{e.status_code}")
    }
  }
}

;; ─── Σ: IMPLEMENTATION CHECKLIST ───
⟦Σ:Checklist⟧{
  NewEndpoint≜{
    ☐ Read OpenAPI spec for endpoint details,
    ☐ Check existing code patterns in similar endpoints,
    ☐ Add function signature with full type hints,
    ☐ Implement using factory pattern (_get_client context manager),
    ☐ Use build_url for URL construction,
    ☐ Apply @handle_request_errors decorator,
    ☐ Parse response with parse_json_response,
    ☐ Add to __init__.py exports,
    ☐ Write test class with parametrized tests,
    ☐ Mock HTTP with httpx_mock fixture,
    ☐ Test happy path + error cases,
    ☐ Run pytest + pyright type checking,
    ☐ Verify coverage≥98%
  }

  Testing≜{
    ☐ Use configure_client fixture for setup,
    ☐ Mock all HTTP calls with httpx_mock,
    ☐ Use build_url for expected URLs,
    ☐ Parametrize similar test cases,
    ☐ Test configuration errors,
    ☐ Test all status code error paths,
    ☐ Test pagination for list endpoints,
    ☐ Verify request method/headers/body,
    ☐ Assert response parsing correct
  }

  Models≜{
    ☐ Inherit from BaseModel (Pydantic),
    ☐ Use Field() for validation constraints,
    ☐ Add full type hints,
    ☐ Use Option⟨T⟩ for optional fields,
    ☐ Document field meanings,
    ☐ Export from models.__init__
  }
}

;; ─── Ε: EVIDENCE ───
⟦Ε⟧⟨
coverage≜0.98
|endpoints|≜50+
|tests|≜200+
|models|≜20+
type_safety≜complete
⊢FP:functional_factory_pattern
⊢DRY:no_duplication,fixtures,parametrization
⊢SOLID:single_responsibility,open_closed,dependency_inversion
⊢HTTP:httpx,context_managers,auth_headers
⊢Models:pydantic,validation,type_hints
⊢Tests:pytest,httpx_mock,isolation,parametrization
⊢Errors:hierarchy,context,status_mapping
⊢Pagination:iterators,lazy_evaluation
⊢Config:module_level,env_vars,getters_setters
⊢JSON_API:resources,relationships,meta,links
python≜3.14+
deps≜{httpx≥0.28.1,pydantic≥2.12.5}
dev_deps≜{pytest≥9.0.2,pytest-cov≥7.0.0,pytest-httpx≥0.36.0,pyright≥1.1.408}
⊢production_ready
⟩
