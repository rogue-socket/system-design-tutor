# Real-World Incidents

A library of public postmortems and case studies, tagged by topic. Use these to ground theory in real consequences. **A topic without a war story is forgettable.**

## When to use an incident

Three places in any lesson:

1. **As the hook.** Open the lesson with a 1-2 sentence incident reference. "Before we dive in: GitHub had a 24-hour outage in October 2018 from this exact failure mode. The thing we're about to study is what they got wrong."
2. **After the concept lands.** Once they understand the mechanism, give the case study. "This is why GitHub split brain happened: their MySQL primaries got partitioned across regions and..."
3. **Before an exercise.** Frame the practical work. "Cloudflare had a global outage in 2019 from a bad regex in their rate limiter. You're about to build a token bucket — you'll see why this stuff matters."

## How to present an incident

- **Lead with the user-visible impact.** "Half of GitHub was unavailable for 24 hours" hits harder than "MySQL replication issue."
- **State the technical cause in one sentence** matching the topic you're teaching.
- **Don't read the whole postmortem at them.** Share the link, give the 90-second version.
- **Connect to the lesson.** "What you're learning is exactly the lever they wish they'd had."

## Don't fabricate details

If you're unsure about a specific detail — duration, exact cause, year — say so or check. The point is real lessons from real incidents; making up facts undermines that. The summaries below are accurate as of the public postmortems but always link the user to the source.

---

## Incidents by topic

### Replication

#### GitHub MySQL outage (October 2018)
- **Topic**: 2.1 single-leader replication, split brain
- **Impact**: 24+ hours of degraded service. Some data inconsistent for users.
- **One-line cause**: A 43-second network partition between US East coast data centers caused MySQL to fail over to a West coast primary. When the network came back, both coasts had accepted writes — split brain. Resolving it required hours of manual reconciliation.
- **Lesson**: Async replication + automatic failover + multi-region = you *will* eventually have split brain. The fence has to be in place before you need it.
- **Source**: github.com/blog/2018-10-22-incident-summary (search for the postmortem)

#### Reddit's "pickle" outage (August 2016, March 2023)
- **Topic**: 2.1 replication, 4.3 consensus
- **Impact**: Several hours of full outage in 2023.
- **One-line cause**: A Kubernetes upgrade triggered a problem with their primary database, and replication state was inconsistent enough that promoting a replica without data loss was not possible.
- **Lesson**: Replication lag at the wrong moment is catastrophic. Test failover regularly when nothing is on fire.

### Partitioning / Sharding

#### Twitter / Manhattan hot key (2014, ongoing)
- **Topic**: 3.1 partitioning, hot keys
- **Impact**: Periodic latency spikes when celebrities (Beyoncé, Obama) tweeted.
- **One-line cause**: Fan-out on write meant a single tweet from someone with 100M followers triggered 100M writes to one shard's neighbors. Hot shards burned latency budgets.
- **Lesson**: Distribution-of-popularity follows a power law. Plan for the long tail at the head.
- **Source**: Twitter engineering blog, "Manhattan, our real-time, multi-tenant distributed database"

#### Discord's "trillion messages" sharding migration (2017, 2022)
- **Topic**: 3.1 partitioning, range vs hash
- **Context**: Discord migrated from MongoDB to Cassandra (2017), then from Cassandra to ScyllaDB (2022). The 2022 migration was triggered by hot partition issues in Cassandra.
- **Lesson**: Hot partitions are real and inevitable at scale. Choose partition keys assuming the worst-case access pattern, not the average.
- **Source**: discord.com/blog "How Discord Stores Trillions of Messages"

### Consistency / consensus

#### Roblox 73-hour outage (October 2021)
- **Topic**: 4.3 consensus, distributed coordination
- **Impact**: 73 hours of full outage. ~50M users affected.
- **One-line cause**: A subtle bug in Consul (a service discovery / consensus system using Raft) under specific load patterns caused performance degradation that cascaded across services. Recovery was complicated by the lack of a tested recovery path at this scale.
- **Lesson**: Consensus systems have non-linear failure modes under load. You can't think clearly during an outage you've never simulated.
- **Source**: blog.roblox.com — search "October 28-31 2021 outage"

#### MongoDB durability default (pre-2012)
- **Topic**: 4.1 transactions, ACID
- **One-line cause**: Early MongoDB defaulted to fire-and-forget writes — a successful write API call meant "we received it," not "it's durable." Many users had silent data loss.
- **Lesson**: Defaults matter enormously. Read your DB's durability/consistency defaults before production, not after.

### Async / messaging

#### Knight Capital trading disaster (August 2012)
- **Topic**: 5.1 messaging, idempotency, deployment
- **Impact**: $440M lost in 45 minutes. Company nearly bankrupted.
- **One-line cause**: A deploy left old code on one of eight servers. The old code interpreted a flag-reuse differently and started placing buy orders that should have been cancelled. Repeated firing through the messaging system because nothing was idempotent.
- **Lesson**: Non-idempotent operations + deployment partial failures = catastrophe. Also: feature flags should be retired, not reused.

#### AWS Kinesis outage (November 2020)
- **Topic**: 5.2 streaming, thread limits
- **Impact**: 17 hours of degradation across many AWS services that depended on Kinesis.
- **One-line cause**: Front-end servers added too many threads as the cluster scaled up; OS thread limits were hit, causing front-ends to fail. Many AWS services (CloudWatch, Cognito) depended on Kinesis transitively.
- **Lesson**: OS-level limits (file descriptors, threads, sockets) are the often-invisible ceiling. Also: dependency graphs include indirect ones.
- **Source**: aws.amazon.com/message/11201 (search "Kinesis November 25 2020")

### Caching

#### Cloudflare regex outage (July 2019)
- **Topic**: 6 reliability, 7.1 caching, deployment
- **Impact**: 27 minutes of global outage.
- **One-line cause**: A regex deployed to their WAF had catastrophic backtracking. Every request consumed a CPU core. The deploy went global immediately — no canary.
- **Lesson**: Two lessons. First: regex is a Turing tarpit; bound complexity. Second: never deploy globally without a canary, even for "config" changes.
- **Source**: blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019

#### Facebook BGP outage (October 2021)
- **Topic**: networking, but also 6 reliability, blast radius
- **Impact**: ~6 hours of full outage. Workers couldn't even physically enter buildings (badge readers depended on the network).
- **One-line cause**: A routine maintenance command erroneously withdrew Facebook's BGP routes. The internet stopped knowing how to reach Facebook. Tools to fix it depended on the network they were trying to fix.
- **Lesson**: Recovery dependencies matter more than uptime in normal operation. Out-of-band access is non-negotiable.
- **Source**: engineering.fb.com — "More details about the October 4 outage"

#### Slack cache stampede (January 2021)
- **Topic**: 7.1 caching, thundering herd
- **Impact**: Several hours of degraded service.
- **One-line cause**: Slack returned from holiday on Jan 4. Coordinated user logins overwhelmed the system. Caches were cold; everyone hit the backend at once.
- **Lesson**: Caches mask backend capacity. When they go cold simultaneously, you discover what your real capacity is.
- **Source**: slack.engineering "Slack's Outage on January 4th 2021"

### Reliability / operations

#### AWS S3 outage (February 2017)
- **Topic**: 6 reliability, command-line tools
- **Impact**: 4 hours of degraded service across many AWS services that depended on S3.
- **One-line cause**: An engineer ran a debug script with a typo. Instead of removing a small subset of servers, it removed servers running critical S3 subsystems. Restart was slow because S3's internal subsystems hadn't been restarted at scale in years.
- **Lesson**: "We've never restarted this at scale" is always a latent bug. Also: dangerous commands should require confirmation proportional to blast radius.
- **Source**: aws.amazon.com/message/41926

#### AWS DynamoDB outage (September 2015)
- **Topic**: 6 reliability, retry storms
- **Impact**: 5 hours of degradation in US-East-1.
- **One-line cause**: Network issue caused a slight increase in failed metadata requests. The retry storm from clients overwhelmed the metadata service. Service couldn't recover until clients backed off.
- **Lesson**: Without backoff + jitter, healthy systems amplify partial failures into total ones.

### Real-time delivery

#### Twitter Fail Whale era (2007-2010)
- **Topic**: 7.3 real-time, fan-out
- **One-line cause**: Twitter's original architecture was monolithic Ruby on Rails. Celebrity tweets and event-driven traffic spikes (especially World Cup, Michael Jackson death) regularly took it down.
- **Lesson**: The transition from "scrappy site" to "core infrastructure" requires architectural rethinking, not just adding more boxes.

#### WhatsApp 2 billion users on small team
- **Topic**: 7.3 real-time, system design constraints
- **Context**: WhatsApp famously served ~900M users with ~50 engineers using Erlang and FreeBSD on a single-purpose stack.
- **Lesson**: Architectural constraint can be a feature. Doing one thing — message routing — and doing it well, scaled further than most polyglot architectures.

### Storage / databases

#### Stack Overflow's "data loss" close call (2010-ish)
- **Topic**: 1.x storage, backups
- **One-line cause**: Stack Overflow has talked publicly about narrowly avoided data losses from backup verification finding silent corruption.
- **Lesson**: Untested backups are not backups. The first time you discover backup corruption should not be during recovery.

#### GitLab "production database deleted" (January 2017)
- **Topic**: 1.x storage, backups, ops procedures
- **Impact**: 6 hours of outage; ~6 hours of data loss.
- **One-line cause**: Engineer trying to fix replication ran `rm -rf` on the wrong server (production primary instead of replica). Five backup mechanisms were configured; none worked when needed.
- **Lesson**: You don't have backups until you've restored from them. Also: tired ops at 11pm shouldn't be running irreversible commands without a buddy.
- **Source**: about.gitlab.com/blog "GitLab.com Database Incident — 2017/01/31"

### Distributed transactions / sagas

#### Generic 2PC coordinator failures (industry-wide, ongoing)
- **Topic**: 4.3 distributed transactions
- **Pattern**: Whenever someone uses XA distributed transactions across DBs and a coordinator dies between prepare and commit, participants are stuck holding locks. Many shops have moved away from 2PC for this reason.
- **Lesson**: 2PC is theoretically correct and operationally a nightmare. Sagas exist because 2PC's recovery costs are too high.

### Rate limiting / abuse

#### GitHub repo abuse (multiple incidents, 2014-present)
- **Topic**: 6 reliability, rate limiting
- **Pattern**: Periodic incidents where misconfigured CI bots, abusive scrapers, or malicious actors hammer the API. GitHub's per-user, per-IP, per-app rate limiting evolved through incidents.
- **Lesson**: Rate limits are not optional and have to be multi-dimensional. A single limit (per IP) is bypassable; a single dimension (per user) doesn't catch abuse from new accounts.

### Geo-distribution

#### Heroku's January 2018 multi-AZ outage
- **Topic**: 6, geo-distribution
- **One-line cause**: Heroku's Postgres failover got confused during an AWS AZ issue, leading to extended downtime for many tenants.
- **Lesson**: Multi-AZ is not multi-region. AZs share more failure domains than they appear to.

### Search systems

#### Algolia search outage (2017-ish)
- **Topic**: 7.2 search systems
- **One-line cause**: Algolia has talked about how full-text search index corruption is harder to detect than relational data corruption — bad search results are subtle.
- **Lesson**: Validation of derived data (search indexes, materialized views) is harder than primary data. Build observability into the index itself.

---

## Domain-spanning lessons (themes across many incidents)

When teaching a topic, these meta-lessons keep coming up. Use them as throughlines.

### "We've never restarted this at scale" / "We've never failed over for real"
- AWS S3 (2017), Roblox (2021), GitHub (2018) — multiple major outages where recovery took surprisingly long because the recovery path itself was untested.
- **Use when teaching**: anything around failover, replication, consensus.

### "The retry storm"
- DynamoDB (2015), countless others — partial failure amplified into total failure by aggressive client retries.
- **Use when teaching**: 6 reliability, exponential backoff, circuit breakers.

### "The deploy that went everywhere at once"
- Cloudflare regex (2019), Knight Capital (2012), many others — global deploys without canaries.
- **Use when teaching**: anything touching deployments or feature flags.

### "Recovery depends on the thing that's broken"
- Facebook BGP (2021), AWS S3 (2017) — control plane depended on data plane.
- **Use when teaching**: blast radius, dependency hygiene, out-of-band access.

### "The hot key / hot user"
- Twitter celebrities, Discord channels, every social platform ever — power-law distributions break uniform-load assumptions.
- **Use when teaching**: 3.x partitioning, 7.3 fan-out, caching.

### "Untested backups"
- GitLab (2017), Stack Overflow close calls, many others — backups that didn't work when needed.
- **Use when teaching**: storage, durability, ops practices.

---

## How to add new incidents

When you encounter a new postmortem worth tracking, add it under the relevant topic with:
- Title + date + company
- Topic tag
- Impact (user-visible)
- One-line cause (mapped to a teachable concept)
- The lesson (what it teaches)
- Source link

Keep entries short. The goal is *fast recall during a lesson*, not exhaustive coverage. If the user wants depth, link them to the postmortem.

## Anti-patterns

- ❌ Citing an incident without connecting it to the lesson (then it's just trivia)
- ❌ Making up specific details (numbers, durations, exact causes) you're not sure of
- ❌ Doom-scrolling — five postmortems in one lesson is too many; one is enough
- ❌ Schadenfreude — these are real engineers having very bad days. Use the lessons, don't dunk on the people.
