# AI Agent for Logistics Automation

A 7-day pilot project implementing an autonomous AI agent for logistics operations with return-triggered restocking, NLP chatbot for order queries, and human-in-the-loop fallback system.

## 🎯 Project Overview

This AI agent autonomously handles:
- **Return-triggered restocking**: Automatically creates restock requests when returns exceed thresholds
- **Order query chatbot**: Answers customer questions about order status and product availability
- **Smart decision making**: Makes basic decisions with confidence scoring
- **Human-in-the-loop fallback**: Escalates low-confidence decisions to human reviewers

## 📊 Key Performance Indicators (KPIs)

### Automation Metrics
- **Restock Decision Speed**: Target <5 minutes (vs 2-4 hours manual)
- **Query Resolution Time**: Target <30 seconds (vs 5-15 minutes manual)
- **Decision Accuracy**: Target >85% auto-approval rate
- **Human Review Rate**: Target <30% of decisions requiring review

### Quality Metrics
- **False Positive Rate**: <10% incorrect restock decisions
- **Customer Satisfaction**: >90% for chatbot interactions
- **System Uptime**: >99% availability

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Excel Data    │    │   AI Agent      │    │ Human Review    │
│                 │    │                 │    │                 │
│ • orders.xlsx   │───▶│ • Sense         │───▶│ • Confidence    │
│ • returns.xlsx  │    │ • Plan          │    │   Scoring       │
│ • inventory.xlsx│    │ • Act           │    │ • Review UI     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   FastAPI       │              │
         │              │   Endpoints     │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Audit Logs    │    │   Chatbot       │    │   Escalation    │
│                 │    │                 │    │                 │
│ • logs.csv      │    │ • Rule-based    │    │ • Email alerts  │
│ • review_log.csv│    │ • OpenAI GPT    │    │ • Manual review │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for smart chatbot)

### Installation

1. **Clone and setup**:
```bash
cd ai-agent_project
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Run the agent**:
```bash
# Run main agent (checks returns and creates restocks)
python agent.py

# Start API server
uvicorn api_app:app --reload

# Start chatbot (rule-based)
python chatbot_agent.py

# Start smart chatbot (OpenAI-powered)
python smart_chatbot.py

# Human review interface
python review_interface.py
```

## 📁 Project Structure

```
ai-agent_project/
├── agent.py                 # Main agent logic (Sense→Plan→Act)
├── api_app.py              # FastAPI endpoints for data access
├── chatbot_agent.py        # Rule-based chatbot
├── smart_chatbot.py        # OpenAI-powered chatbot
├── human_review.py         # Human-in-the-loop system
├── review_interface.py     # CLI for human reviewers
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── data/
    ├── orders.xlsx        # Order status data
    ├── returns.xlsx       # Product return data
    ├── restock_requests.xlsx  # Generated restock requests
    ├── logs.csv          # Agent action audit log
    ├── review_log.csv    # Human review decisions
    └── pending_reviews.json  # Pending human reviews
```

## 🔄 Workflow Details

### 1. Return-Triggered Restocking

**Process Flow**:
1. **Sense**: Read `returns.xlsx` for new return data
2. **Plan**: Check if return quantity > threshold (default: 5)
3. **Act**: Create restock request or submit for human review

**Confidence Scoring**:
- High confidence (>0.7): Auto-execute
- Medium confidence (0.4-0.7): Log and execute with monitoring
- Low confidence (<0.4): Require human review

**Example**:
```python
# Returns data triggers restock
ProductID: A101, ReturnQuantity: 6 → Auto-restock (high confidence)
ProductID: B202, ReturnQuantity: 25 → Human review (low confidence - unusual quantity)
```

### 2. Order Query Chatbot

**Supported Queries**:
- "Where is my order #123?" → Returns order status
- "When will Product A101 be restocked?" → Returns restock information
- Complex queries → Escalated to human support

**Response Examples**:
```
User: "Where is my order #101?"
Bot: "📦 Your order #101 is: Shipped."

User: "This is urgent! My order is missing!"
Bot: "🔄 Your query has been forwarded to our support team for personalized assistance. Reference ID: chatbot_response_20250807_143022"
```

### 3. Human-in-the-Loop System

**Review Triggers**:
- Restock quantities >20 units
- Products without historical data
- Customer queries containing "urgent", "emergency", "complaint"
- Any decision with confidence <70%

**Review Interface Commands**:
```bash
# Start review interface
python review_interface.py

# Available commands:
list        # Show pending reviews
review <id> # Review specific decision
auto        # Auto-review all (demo mode)
stats       # Show review statistics
```

## 📈 Current Performance

### Completed Features ✅
- [x] Excel data pipeline with pandas
- [x] FastAPI endpoints for data access
- [x] Agent logic with Sense→Plan→Act pattern
- [x] Audit logging system
- [x] Rule-based chatbot
- [x] OpenAI-powered smart chatbot
- [x] Human review system with confidence scoring
- [x] CLI review interface

### Test Results 📊
```
Agent Performance:
- Processed 2 return events
- Generated 2 restock requests (A101: 6 units, C303: 8 units)
- 100% auto-approval rate (high confidence decisions)
- Average processing time: <1 second

Chatbot Performance:
- Handles order status queries: ✅
- Handles restock queries: ✅
- Escalates complex queries: ✅
- Response time: <30 seconds
```

## 🔧 Configuration

### Thresholds
```python
# agent.py
THRESHOLD = 5  # Minimum returns to trigger restock

# human_review.py
confidence_threshold = 0.7  # Minimum confidence for auto-approval
```

### Data Schema
```python
# orders.xlsx
OrderID (int), Status (string)

# returns.xlsx
ProductID (string), ReturnQuantity (int)

# restock_requests.xlsx
ProductID (string), RestockQuantity (int)
```

## 🚨 Known Issues & Limitations

### Current Limitations
1. **Single Excel file processing**: No concurrent access handling
2. **Basic confidence scoring**: Could be enhanced with ML models
3. **Limited chatbot NLP**: Rule-based parsing for complex queries
4. **No real-time notifications**: Human reviewers must check manually

### Security Considerations
- OpenAI API key stored in environment variables
- No authentication on FastAPI endpoints
- Local file storage (not production-ready)

## 🛣️ Roadmap (Week 2+)

### Immediate Improvements
- [ ] Add email notifications for pending reviews
- [ ] Implement real-time dashboard
- [ ] Add unit tests and integration tests
- [ ] Database integration (replace Excel files)

### Advanced Features
- [ ] Machine learning for confidence scoring
- [ ] Inventory forecasting agent
- [ ] Delivery tracking integration
- [ ] Multi-tenant support

### Scalability
- [ ] Containerization with Docker
- [ ] Message queue for async processing
- [ ] Monitoring and alerting
- [ ] Load balancing for API endpoints

## 📞 Support

For questions or issues:
1. Check the logs in `data/logs.csv`
2. Review pending items in `data/pending_reviews.json`
3. Use the review interface: `python review_interface.py`

## 📄 License

This is a pilot project for internal use. All rights reserved.
