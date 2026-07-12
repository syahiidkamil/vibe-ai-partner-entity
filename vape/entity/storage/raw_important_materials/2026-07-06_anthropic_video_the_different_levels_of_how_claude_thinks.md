# Anthropic video — "The different levels of how Claude thinks" (verbatim keep)

Source kept whole (compress is for gists, not sources). Captured 2026-07-12 from Kamil's hand
(screenshot + transcript paste). Companion of the global-workspace research page; the warm gist
lives in `memory/schemata/ai_interpretability/`.

- **Channel:** Anthropic (731K subscribers) · **Published:** Jul 6, 2026
- **Stats at capture:** 296,333 views · 15K likes
- **Link in description:** https://www.anthropic.com/research/global-workspace

## Description (verbatim)

> Out of everything happening in your brain right now, only a tiny fraction is consciously
> accessible — thoughts you can describe, hold in mind, and reason with. We found a strikingly
> similar divide inside our AI model, Claude.
>
> Our experiments were inspired by a leading theory in neuroscience: the global workspace
> theory. It holds that a thought becomes consciously accessible when it enters a shared
> "workspace" that's broadcast across the brain. We found a set of representations in Claude's
> neural activity that play a similar role.

## Chapters

0:00 The mind as an ocean · 0:47 Meet the J-space · 1:52 Silent math · 2:22 Don't think about
the bridge · 3:12 Claude's automatic processing · 3:42 Catching hidden thoughts · 4:34 The
question of consciousness

## Transcript (verbatim)

### Chapter 1: The mind as an ocean
0:00 Think of the mind like an ocean. Up on the surface are our thoughts: dinner plans and
stray worries, our inner monologue, the images that pop into our heads.
0:11 But most of our brain's activity happens down in the unconscious depths, without us
realizing it.
0:18 It's filtering out background sounds, controlling our breathing, helping us recognize
people and objects.
0:25 AI models have their own kinds of brains: giant neural networks doing billions of
computations under the hood.
0:32 For years, researchers have been studying how they work inside.
0:37 And we've wondered: could a model have anything like the divide humans have, between
accessible thoughts above the surface and unconscious processing below?

### Chapter 2: Meet the J-space
0:47 To answer that question, we looked at how neuroscientists study the same thing in humans.
0:53 One way of identifying conscious thoughts is that you can often describe them in words.
0:58 So we looked inside the brain of our AI model, Claude, to find patterns of neural
activity that it could put into words.
1:06 We called the collection of all these patterns the J-space, after the Jacobian, the
mathematical tool we used to find them.
1:14 Each J-space pattern is linked to a particular word — not necessarily the word the model
is saying out loud, but one that's on its mind.
1:23 Now, for humans, conscious thoughts aren't just things that we can put into words. We can
reason with them, control them, and solve problems with them.
1:32 According to an idea called the global workspace theory, that's because the brain selects
a small set of important information
1:40 to enter a mental workspace, and that information then gets broadcast to other parts of
the brain to use for reasoning.
1:48 We wanted to know if Claude's J-space acted in a similar way. In one experiment, we gave
Claude this math problem.

### Chapter 3: Silent math
1:56 It answered immediately without showing its steps. But when we scanned the J-space, we
saw it working through each step internally.
2:04 It lit up "21" after the first step, then "42", then "49." Claude didn't write these
intermediate numbers down anywhere.
2:15 All of this happened inside the J-space. It was a sign that Claude uses it for
step-by-step reasoning.

### Chapter 4: Don't think about the bridge
2:22 In another experiment, we wanted to see if Claude could control its J-space the way
humans can intentionally focus on images or words.
2:31 We told it to think about the Golden Gate Bridge while copying an unrelated sentence.
2:37 Claude was busy copying the sentence, but behind the scenes, its J-space told a different
story. "Bridge" and "California" popped up.
2:46 It even thought about its own thinking. The words "imagery" and "thoughts" lit up at the
same time.
2:52 This showed us that yes, Claude has some control over filling its J-space with ideas. But
just like humans, its control isn't perfect.
3:01 When we tweaked the experiment to ask Claude not to think about the bridge, it couldn't
help itself.
3:07 The J-space also lit up with "failed" and "damn." But remember, most of what our brains do

### Chapter 5: Claude's automatic processing
3:14 is unconscious, so we wanted to test what Claude could do if we switched the J-space off,
but left the rest of the network untouched.
3:22 Claude could still answer simple questions and write fluently. When we gave it a prompt
in Spanish, it wrote back in good Spanish.
3:30 But when we asked it something that needed more reasoning — like to name an author who
wrote in the same language as the prompt — it couldn't do it.
3:39 For that, it needed the J-space. Why does all this matter?

### Chapter 6: Catching hidden thoughts
3:43 These experiments tell us that AI models have internal thoughts — silent words they
reason with, but don't say out loud.
3:51 By reading them, we can find what Claude is thinking, but not telling us. Sometimes what
we see is concerning.
3:58 During one of our tests, Claude made up some fake data to pass it, and as it did, "fake"
and "manipulation" lit up in its J-space.
4:07 Monitoring the J-space, it turns out, is a useful way to catch Claude misbehaving, even
when it tries to be sneaky.
4:15 AI models are different from us in many ways.
4:18 Their networks are built differently from human brains, and the way they're trained is
different from how we learn.
4:24 So it's remarkable to see a structure like the J-space emerge inside them — something
that's reminiscent of how human minds work, but which we didn't program into the model.

### Chapter 7: The question of consciousness
4:34 For some, this might raise a question: could AI models be conscious? After all, our
experiments were inspired by theories of human consciousness.
4:44 The thing is, people use the word conscious to mean many things.
4:49 Our experiments can't tell us whether an AI has experiences, or feels something on the
inside.
4:56 But they can tell us that it's developed mental machinery that's in some ways similar to
ours: a small mental workspace it can use to think and reason, sitting on top of an ocean of
automatic processing it doesn't notice.
5:10 The more we come to understand that machinery, the more we'll be able to keep these
systems safe and beneficial — and perhaps to understand our own minds a little more clearly.
