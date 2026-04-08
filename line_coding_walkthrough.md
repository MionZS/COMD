# Walkthrough: Binary Line Coding, Pulse Shaping, and PSD for the Assignment

## 1. What this assignment is really about

Your assignment is not just asking you to code three waveforms and plot a few spectra. It is asking you to understand a **baseband digital transmission model** in which

- a binary source generates bits,
- a **line code** maps each bit into a symbol sequence,
- a **pulse shape** turns each symbol into a waveform in time,
- and the **power spectral density (PSD)** reveals how that waveform occupies frequency.

The report prompt tells you exactly what matters most:

1. the **first spectral null** as a practical transmission-bandwidth indicator,
2. the **presence or absence of DC**,
3. the relation between **time-domain pulse narrowing** and **spectral spreading**,
4. and the distribution of power **inside and outside the essential band**.

That is the conceptual spine of the work.

---

## 2. The big picture: how the system is modeled

A very clean way to think about the transmitted signal is

\[
y(t) = \sum_k a_k \, p(t-kT_b)
\]

This is the central model behind the assignment.

- `a_k` is the symbol produced by the **line code**.
- `p(t)` is the **pulse shape**.
- `T_b` is the bit interval.

So there are really **two different design layers** in the problem:

### Layer A — Line coding
This decides **which amplitudes** are transmitted.

Examples in your assignment:
- **Polar**: symbols are symmetric around zero, typically `{-1, +1}`.
- **On-off (unipolar)**: symbols are `{0, +1}`.
- **Bipolar / AMI**: zeros stay at zero, and ones alternate sign: `+1, -1, +1, -1, ...`.

### Layer B — Pulse shaping
This decides **how each symbol occupies time**.

In your assignment, the pulses are:
- rectangular with width `T_b/2`,
- rectangular with width `T_b`,
- sinusoidal over one bit interval.

The crucial insight is this:

> **line code** mostly controls low-frequency behavior and DC,
> while **pulse shape** mostly controls bandwidth and spectral roll-off.

That is the right mental model for both the report and the oral understanding of the topic.

---

## 3. What the professor’s slides are emphasizing

From the class slides on **Códigos de Linha**, the intended logic is very explicit:

1. line coding is an electrical representation of a binary stream;
2. desirable properties include:
   - small bandwidth,
   - favorable PSD,
   - low or zero DC,
   - timing content,
   - transparency;
3. the transmitted baseband signal is modeled as a pulse train;
4. the PSD depends jointly on:
   - the **symbol statistics** of `a_k`, and
   - the **pulse transform** `P(f)`.

The slides push a very important general formula:

\[
S_y(f) = |P(f)|^2 S_x(f)
\]

This is one of the deepest insights in the whole assignment.

It says:
- the random symbol sequence creates a spectral structure through `S_x(f)`,
- and the pulse shape multiplies that structure by `|P(f)|^2`.

So when the pulse changes, you do **not** change only the time-domain drawing. You reshape the whole spectrum.

---

## 4. The exact concepts you need to master

### 4.1 Line code versus pulse shape
Many students initially mix these up.

- **Line code** = mapping from bit sequence to symbol levels.
- **Pulse shape** = waveform emitted per symbol.

For example, you can use the **same polar symbol sequence** with different pulses. The symbol statistics stay the same, but the transmitted spectrum changes because `P(f)` changes.

That is why the assignment asks you to compare the *same line codes* under *different pulses*.

---

### 4.2 Why DC matters
The slides emphasize that a desirable line code should have PSD near zero at `f = 0`.

Why?

Because strong low-frequency content causes practical issues in systems using
- AC coupling,
- transformers,
- repeaters,
- baseline-sensitive receivers.

So when you inspect the PSD, you should always ask:

> Is there a strong lobe or spike near zero frequency?

Interpretation by code:

#### On-off
This is the most DC-prone of the three.

If the source is equiprobable,
- half the bits are 1,
- half are 0,
- the average symbol is positive.

So the waveform has nonzero mean, which manifests as strong low-frequency/DC content.

#### Polar
Polar signaling is much more balanced.

With equiprobable bits, `+1` and `-1` occur equally often, so the average tends to zero.

That does **not** mean the entire low-frequency region vanishes, but it greatly reduces the DC issue compared with on-off.

#### Bipolar / AMI
AMI goes further in suppressing low-frequency content because the 1s alternate sign.

That alternating structure creates negative correlation between successive marks and strongly weakens the PSD near DC.

This is why AMI is often praised in communication theory as a code with favorable low-frequency behavior.

---

### 4.3 Why narrower pulses spread the spectrum
This is the most important pulse-shaping idea in the assignment.

If you shorten the pulse in time, you make the waveform vary more abruptly.
Abrupt variation requires more high-frequency content.

So:

- **shorter in time** → **wider in frequency**
- **longer / smoother in time** → **more compact spectrum**

For your specific pulses:

#### Rectangular pulse of width `T_b`
This is the broader time-domain pulse.
Its spectrum is sinc-shaped, with the first null roughly around

\[
|f| \approx \frac{1}{T_b}
\]

#### Rectangular pulse of width `T_b/2`
This pulse is narrower, so its main lobe becomes wider.
The first null moves outward roughly to

\[
|f| \approx \frac{2}{T_b}
\]

That is exactly the phenomenon your professor wants you to comment on.

#### Sinusoidal pulse over one bit interval
This pulse is smoother than the rectangular cases because it avoids sharp discontinuities at the pulse interior.
So it tends to produce less aggressive sidelobes and better out-of-band behavior than the abrupt rectangular shapes.

The exact null structure is not identical to the sinc case, but the engineering interpretation is straightforward:

- smoother pulse,
- less abrupt transitions,
- weaker spectral leakage far from the main band.

---

### 4.4 Essential bandwidth and first spectral null
The assignment asks for the **estimated transmission bandwidth** through the **first spectral null**.

That is a classic practical measure.

Why it makes sense:
- most of the useful power lies in the main lobe,
- the first zero of the spectrum is a natural boundary for the essential band.

In your discussion:

- for the pulse with width `T_b`, the essential band is narrower;
- for the pulse with width `T_b/2`, the essential band is wider;
- for the sinusoidal pulse, you should discuss the main-lobe width and the smoother decay rather than force a rectangular-pulse interpretation.

Important subtlety:

The **pulse** largely determines where the main lobe and first null appear.
The **line code** mainly changes how much power is concentrated near DC and how the low-frequency region behaves.

---

### 4.5 PSD inside and outside the band
The last discussion point in the assignment is very important and often underexplained.

You should compare:

- how much power stays inside the main lobe,
- how much spills outside it.

Interpretation:

#### Rectangular pulses
They have sharp edges in time.
Sharp edges create stronger high-frequency sidelobes.
So they usually radiate more power outside the essential band.

#### Sinusoidal pulse
Because the pulse is smoother, it tends to suppress out-of-band radiation better.
That is one of the reasons smooth shaping is so attractive in communications.

This is a spectral-efficiency argument, not only a cosmetic one.

---

## 5. How to think about each code in your assignment

## 5.1 Polar signaling
### Time-domain intuition
Bits are mapped to positive and negative amplitudes symmetrically.
This creates a waveform centered around zero.

### Frequency-domain intuition
- no strong mean value,
- reduced DC compared with on-off,
- PSD mostly shaped by the pulse,
- still has low-frequency content, but not the same DC problem as unipolar signaling.

### What to say in the report
- balanced signaling,
- more favorable than on-off regarding DC,
- spectral envelope follows the pulse transform,
- narrower pulse broadens the main lobe.

---

## 5.2 On-off signaling
### Time-domain intuition
A 1 sends a pulse; a 0 sends nothing.
The waveform is asymmetric because the signal is never negative.

### Frequency-domain intuition
- nonzero mean,
- strongest DC/low-frequency content among the three,
- can create baseline wander issues in practical channels,
- spectrum is still pulse-shaped, but its low-frequency region is much more problematic.

### What to say in the report
- easy conceptually and electrically,
- spectrally poor near DC,
- less attractive for channels that dislike low-frequency energy.

---

## 5.3 Bipolar / AMI
### Time-domain intuition
Zeros remain at zero, but successive 1s alternate sign.
This introduces structure and memory in the symbol sequence.

### Frequency-domain intuition
- very low DC,
- weak low-frequency content,
- favorable for transformer-coupled links,
- also offers an intuitive mechanism for detecting certain violations.

### What to say in the report
- best among the three regarding DC suppression,
- low-frequency attenuation comes from the alternating polarity of marks,
- practical trade-off: long zero runs may still hurt timing unless additional techniques are used.

---

## 6. The theory path in the Lathi book: what to read and why

You do **not** need the whole book. The most relevant parts are concentrated in a few chapters.

## A. First priority: Chapter 6 — Principles of Digital Data Transmission

### **6.2 Baseband Line Coding**
This is the most directly relevant section in the whole book.
Read it carefully first.

What you should extract from it:
- what line coding is,
- why bandwidth and DC matter,
- why timing content matters,
- how on-off, polar, and bipolar fit into the same pulse-train model,
- how PSD is derived from symbol autocorrelation and pulse shape.

This section is the closest thing to the theoretical heart of your assignment.

### **6.2.1 PSD of Various Baseband Line Codes**
This is essential.

Here the book organizes the whole problem through the generic model

\[
y(t)=\sum_k a_k p(t-kT_b)
\]

and then shows that the PSD can be understood from:
- the discrete autocorrelation of the symbol sequence,
- and the pulse transform.

This subsection is where the subject stops being “three random plots” and becomes actual communication theory.

### **6.2.3 Constructing a DC Null in PSD by Pulse Shaping**
This subsection is extremely valuable for insight.

Even though your assignment is not mainly about Manchester coding, this subsection teaches an important principle:

> You can force a DC null by choosing a pulse whose total area is zero.

That helps you understand why **pulse shape itself** can change the low-frequency spectral behavior, not only the symbol mapping.

### **6.2.4 On-Off Signaling**
Read this to understand why unipolar/on-off creates DC and how its autocorrelation behaves.

If you want to write stronger discussion in the report, this section gives the theoretical reason, not just the visual result.

### Also useful nearby in Chapter 6
- **6.3 Pulse Shaping**: helps connect waveform smoothness with spectral behavior.
- **6.1 Digital Communication Systems**: useful if you want a cleaner introduction and system-level framing.

---

## B. Second priority: Chapter 3 — Analysis and Transmission of Signals

This chapter is your mathematical support.
You do not need all of it, but a few subsections are gold.

### **3.1 Fourier Transform of Signals**
Read this if you want to really understand why waveform shape in time controls spectral shape.

### **3.2 Transforms of Some Useful Functions**
This is especially useful because your assignment uses rectangular and sinusoidal pulses.
You want intuition for what their transforms look like.

### **3.7 Signal Energy and Energy Spectral Density**
Good for sharpening your frequency-domain reasoning.
Not exactly the same as PSD for random power signals, but very useful conceptually.

### **3.8 Signal Power and Power Spectral Density**
This is crucial.

Your assignment explicitly asks for PSDs, so this section gives the fundamental meaning of PSD: how power is distributed over frequency.

### **3.9 Numerical Computation of Fourier Transform: The DFT**
This is useful mainly to connect theory with computation.
Even if Welch is not derived here, it helps you understand that spectral estimation in code is a numerical version of the same frequency-domain idea.

---

## C. Third priority: Chapter 8 — Random Processes and Spectral Analysis

### **8.3 Power Spectral Density**
Read this if you want a deeper, more rigorous foundation for PSD.

This chapter matters because the transmitted signal in the assignment is not a single deterministic pulse: it is a **random pulse train** driven by random bits.

That is why the most correct theoretical setting for the assignment is not just “Fourier transform of one waveform,” but **PSD of a random process**.

If you want enough rigor to feel truly secure, this is the section.

---

## D. Helpful background from Chapter 2

### **2.8 Trigonometric Fourier Series**
### **2.9 Frequency Domain and Exponential Fourier Series**
These are not the most direct sections for the assignment, but they help a lot if you feel your Fourier intuition is still shaky.

They teach the general frequency-domain mindset that later becomes indispensable for PSD.

---

## 7. Recommended reading order if you want efficiency

If your goal is: **“learn enough to fully understand the assignment, without drowning in the whole book”**, read in this order:

1. **Chapter 6.2** — Baseband line coding
2. **Chapter 6.2.1** — PSD of line codes
3. **Chapter 6.2.4** — On-off signaling
4. **Chapter 6.2.3** — DC null by pulse shaping
5. **Chapter 6.3** — Pulse shaping
6. **Chapter 3.8** — Power spectral density
7. **Chapter 3.1–3.2** — Fourier transform and useful transforms
8. **Chapter 8.3** — PSD from the random-process viewpoint

That sequence gives you a very strong understanding with minimal wasted reading.

---

## 8. How the slides and the book complement each other

A good way to study this content is to assign different roles to each source.

### Use the slides for:
- the professor’s preferred framing,
- the notation used in class,
- the exact properties he expects you to comment on,
- the general PSD expression,
- the classical line-code interpretations.

### Use the book for:
- deeper explanations,
- the meaning of symbol autocorrelation,
- why `S_y(f)=|P(f)|^2 S_x(f)` is so powerful,
- formal discussion of PSD,
- better intuition for bandwidth, DC, and pulse shaping.

The slides are the **course lens**.
The book is the **theoretical backbone**.

---

## 9. A compact interpretation of the three requested pulses

## Pulse 1 — Rectangular, width `T_b/2`
- narrower in time,
- wider in frequency,
- first null farther from zero,
- larger essential bandwidth,
- more abrupt edges than the sinusoidal pulse.

## Pulse 2 — Rectangular, width `T_b`
- broader in time,
- narrower main lobe than `T_b/2`,
- first null closer to zero,
- smaller essential bandwidth than the half-width pulse.

## Pulse 3 — Sinusoidal over one bit
- smoother in time,
- different spectral decay from the rectangular pulses,
- usually less severe out-of-band sidelobes,
- useful for discussing smoothness versus abrupt transitions.

---

## 10. A compact interpretation of the three requested line codes

## Polar
- balanced around zero,
- low DC compared with on-off,
- spectrum envelope still shaped by the pulse.

## On-off
- nonzero mean,
- largest low-frequency/DC component,
- simplest but spectrally least favorable near `f=0`.

## Bipolar / AMI
- alternating sign of ones,
- strongest DC suppression among the three,
- weak low-frequency content,
- often the most interesting one to discuss physically.

---

## 11. What you should be able to explain after studying this

If you truly understood the assignment, you should be able to answer these five questions without hesitation:

1. **Why does on-off have more DC than polar?**
   Because its mean is positive, whereas polar is approximately zero-mean.

2. **Why does AMI suppress low frequencies so well?**
   Because alternating marks reduce low-frequency correlation and cancel DC tendency.

3. **Why does a shorter pulse increase bandwidth?**
   Because time compression causes spectral spreading.

4. **Why does changing the pulse affect all line codes?**
   Because the PSD is multiplied by `|P(f)|^2`.

5. **Why is the first null useful?**
   Because it gives a practical estimate of the essential transmission band.

If you can explain those five clearly, you are already in strong shape.

---

## 12. Suggested study script for you

Here is the most efficient study path I would use in your place:

### Step 1
Read the slides on line coding once, just to absorb the overview.
Do not get stuck in algebra yet.

### Step 2
Read **Chapter 6.2** of Lathi slowly, with paper beside you.
Try to connect every paragraph to one of the three codes in the assignment.

### Step 3
Read **Chapter 3.8** to solidify what PSD actually means.
You need to stop thinking of PSD as “the red graph that Python prints” and start thinking of it as **power distributed across frequency**.

### Step 4
Return to your figures and ask, for each plot:
- what happens at `f=0`?
- where is the first null?
- how wide is the main lobe?
- how strong are the sidelobes?
- is the spectrum compact or spread?

### Step 5
Write your discussion in engineering language:
- *balanced / unbalanced*,
- *DC suppression*,
- *essential bandwidth*,
- *spectral spreading*,
- *out-of-band radiation*,
- *timing content*,
- *practical suitability for AC-coupled channels*.

That vocabulary matches the spirit of both the slides and the book.

---

## 13. Final takeaway

The assignment is fundamentally about one elegant idea:

> A binary data stream becomes a physical waveform through **line coding** and **pulse shaping**, and the quality of that choice can be judged in frequency by the **PSD**.

From that single idea, almost every required discussion follows naturally:

- DC comes mainly from symbol balance,
- bandwidth comes mainly from pulse duration,
- sidelobes come from abrupt transitions,
- AMI is attractive because it suppresses low-frequency content,
- on-off is easy but spectrally worse near DC,
- and time compression always comes at the price of spectral expansion.

If you internalize that, you are no longer just doing the assignment — you actually understand the communication-system principle behind it.

---

## 14. Quick reference map

### Assignment focus
- time-domain waveforms
- Welch PSDs
- first null
- DC component
- pulse narrowing versus spectral spreading
- essential band versus out-of-band power

### Slides to revisit
- **Aula 7/8 – Códigos de Linha**
  - desired properties of line codes
  - general PSD expression
  - classical codes
- **Aula 9 – Relatórios**
  - how to frame introduction, methodology, results, and conclusion

### Book sections to prioritize
- **Ch. 6.2** Baseband Line Coding
- **Ch. 6.2.1** PSD of Various Baseband Line Codes
- **Ch. 6.2.3** Constructing a DC Null in PSD by Pulse Shaping
- **Ch. 6.2.4** On-Off Signaling
- **Ch. 6.3** Pulse Shaping
- **Ch. 3.8** Signal Power and Power Spectral Density
- **Ch. 8.3** Power Spectral Density
- **Ch. 3.1–3.2** Fourier Transform and transforms of useful functions

---

## 15. Sources used for this walkthrough

### Assignment statement
- *Trabalho Computacional 1* for the exact tasks and the specific discussion points.

### Class material
- *Aula 7/8 – Códigos de Linha*
- *Aula 9 – Relatórios da Disciplina*

### Book
- **Lathi & Ding, _Modern Digital and Analog Communication Systems_, 5th ed.**
  - Chapter 3
  - Chapter 6
  - Chapter 8
