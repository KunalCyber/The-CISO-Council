# I Built a Virtual CISO Council That Debates Real Cybersecurity Dilemmas

Every security leader I know has been in this situation: you are facing a decision with real consequences, you have incomplete information, the clock is running, and the people around you either agree with whatever you say or are too removed from the technical reality to push back meaningfully.

The boardroom pressure-tests you eventually. The regulator pressure-tests you. The incident does. But by then, it is too late to refine your thinking.

That problem is what I built The CISO Council to solve.

---

## The Idea

Andrej Karpathy built an [LLM Council](https://github.com/karpathy/llm-council) as a general multi-model debate framework. I wanted something specific: a council of AI models that reason like experienced security professionals, each with a different organisational context, risk appetite, and regulatory lens, debating the same real-world dilemma.

Not a chatbot. Not a compliance tool. A structured adversarial deliberation engine.

The premise is simple: assign each model a different persona, send them the same scenario, score every response on dimensions that actually matter in security practice, and surface where they agree, where they split, and what that split tells you about the decision.

A fintech CISO with a risk appetite of 4 does not reason the same way as a bank CRO with an appetite of 1. A DPO who thinks about GDPR enforcement actions daily brings different instincts to a vendor breach than a head of internal audit from manufacturing. Those differences are not just interesting: they are the point. The value is in the tension.

---

## What It Actually Does

You submit a scenario. It can be a pre-built YAML file or a custom dilemma you type directly into the War Room UI.

Six AI models receive the same prompt, each with a distinct system prompt encoding their persona: their professional background, their organisational context, their regulatory lens, and their decision-making style. They deliberate independently.

A separate scoring model (Gemini 2.5 Flash by default) then evaluates each response on five dimensions:

- **Regulatory defensibility**: Would this hold up under scrutiny from a regulator?
- **Practicality**: Can this be implemented with realistic resources and timelines?
- **Board-readiness**: Could you present this recommendation to a board without a translator?
- **Specificity**: Concrete named actions, or vague gestures at "best practice"?
- **Risk quantification**: Does it frame risk in business terms, or purely in technical ones?

A synthesis model then reads all six scored responses and produces a consensus/dissent analysis: where the council broadly agrees, where one or more members take a materially different position, and what the disagreement reveals about the decision's complexity.

The output is a structured council report, exportable as a PDF you could hand to someone.

---

## Who This Is For

I want to be direct about this: The CISO Council is not a GRC tool. It is not a compliance automation platform. It is not a checklist generator.

It is for anyone who makes security decisions.

That includes CISOs preparing for a board conversation. Security architects stress-testing a design trade-off. Incident responders working through response options at 2am. Risk managers trying to understand how different risk appetites frame the same exposure. Penetration testers preparing a finding and wondering how a CRO would read it. Security consultants who want to pressure-test a recommendation before they deliver it to a client.

It is also for students and early-career practitioners who want to see how experienced security leaders reason differently about the same problem. That is one of the hardest things to learn without just sitting in a lot of rooms with senior people for years.

---

## Free to Start, Better With Frontier Models

The free tier uses Gemini, Llama via Groq, Mistral, and Cerebras. Total cost: nothing. You can run a full council session on a real scenario in under three minutes.

But here is the honest version: the quality difference when you use frontier models is significant.

When you put Claude Opus in one seat, GPT-4o in another, Gemini 2.5 Pro, Grok-3, and o3 around the table, the responses are materially better. The reasoning is deeper. The recommendations are more specific. The dissent is more interesting. The consensus analysis becomes genuinely useful, not just competent.

The free setup is enough to understand what the tool does and whether it is useful for you. The production setup is what you want when you are using it to inform a real decision.

---

## The Scenarios Matter

The tool is only as good as the scenarios you feed it.

Generic scenarios produce generic responses. "Your company experienced a data breach: what do you do?" tells the council nothing specific enough to disagree about. Every persona will say roughly the same thing.

Good scenarios force a position. They have real constraints, specific numbers, an unresponsive vendor, a 72-hour notification window that may already be running, a board expecting a status update in eight hours. Reasonable security professionals should be able to disagree about the right call.

The three scenarios I have built so far are deliberately hard:

- A vendor breach where the vendor has gone silent and you cannot confirm scope before the regulatory clock expires
- A cloud migration with 14 open high-severity findings and executive pressure to proceed
- An AI credit scoring model with a 12% demographic disparity that also outperforms the existing system by 23%

None of these have clean answers. That is the point.

---

## What I Learned Building It

Three things stood out.

First, the persona design matters more than the model choice at lower quality tiers. A well-constructed system prompt that encodes organisational context, risk appetite, and regulatory lens produces meaningfully different reasoning from the same model. You do not need six different providers to get six different perspectives, though it helps.

Second, scoring is genuinely hard. Getting a model to return consistent, calibrated, well-reasoned scores across five dimensions requires both a good rubric and the right technical setup. JSON mode, temperature zero, and a clear scoring prompt are all necessary. Without them you get every score at 5.0 and no signal at all.

Third, the dissent is more valuable than the consensus. Consensus points are reassuring. Dissent points tell you where the decision is actually risky, where your context determines which answer is right, and where a practitioner in a different organisation would push back on your instinct.

---

## What Is Next

More scenarios. Better personas for sectors I have not covered: government, energy, defence, retail. The ability to add your own personas via config. Tighter scoring rubrics calibrated against practitioner judgment.

The War Room UI is functional but still early. The PDF export works. The scoring and consensus synthesis work when you have the right API keys configured.

If you are a security practitioner and you want to contribute scenarios from your experience, that is the thing I most want. Real dilemmas, anonymised as needed, specific enough to force a real position.

---

The CISO Council is open-source. The code is on GitHub. The setup takes ten minutes. Run it against a decision you are actually facing and see if the output tells you something you had not considered.

That is the only test that matters.

---

**Kunal RK** — [LinkedIn](https://www.linkedin.com/in/kunal-rk-a255aa301/) | [GitHub](https://github.com/kunal-rk)
