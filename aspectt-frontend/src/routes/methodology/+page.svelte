<svelte:head><title>Methodology - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Pipeline methodology</h1>

	<div class="card">
		<p class="intro">
			ASPECTT (A System for Profiling Employment Characteristics and Transferable Traits) translates the US
			<a href="https://www.onetonline.org" target="_blank" rel="noopener">O*NET</a> occupational database
			into a UK-contextualised equivalent, mapped to the UK Standard Occupational Classification (SOC) 2020 framework.
		</p>
	</div>

	<div class="card">
		<h2>1. Data sources</h2>
		<div class="table-wrap">
			<table>
				<thead>
					<tr><th>Source</th><th>Version</th><th>Description</th></tr>
				</thead>
				<tbody>
					<tr><td>US O*NET</td><td>v30.2</td><td>923 occupation profiles with skills, abilities, knowledge, tasks, technology skills, interests, work values, education requirements, and more</td></tr>
					<tr><td>BLS SOC 2010 &harr; 2018 crosswalk</td><td>2018</td><td>Maps between the 2010 and 2018 editions of the US Standard Occupational Classification</td></tr>
					<tr><td>BLS ISCO-08 &harr; SOC 2010 crosswalk</td><td>&ndash;</td><td>Maps between the International Standard Classification of Occupations (ISCO-08) and US SOC 2010</td></tr>
					<tr><td>ONS SOC 2020 coding index</td><td>2025-03-12</td><td>UK SOC 2020 framework (412 unit groups) with embedded ISCO-08 codes</td></tr>
				</tbody>
			</table>
		</div>
	</div>

	<div class="card">
		<h2>2. Crosswalk construction</h2>
		<p>The pipeline builds a four-step crosswalk chain to bridge US and UK classification systems:</p>
		<div class="crosswalk-chain">
			<span class="chain-step">O*NET SOC</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">US SOC 2018</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">US SOC 2010</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">ISCO-08</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">UK SOC 2020</span>
		</div>

		<h3>Step 1 &ndash; O*NET SOC &rarr; US SOC 2018</h3>
		<p>O*NET codes (e.g. <code>15-1252.00</code>) are truncated to their 6-digit base SOC code (<code>15-1252</code>), which maps directly to the US SOC 2018 system.</p>

		<h3>Step 2 &ndash; US SOC 2018 &rarr; US SOC 2010</h3>
		<p>The BLS provides a crosswalk between the 2018 and 2010 editions. This is a many-to-many mapping (occupations were split and merged between editions).</p>

		<h3>Step 3 &ndash; US SOC 2010 &rarr; ISCO-08</h3>
		<p>The BLS provides a crosswalk between US SOC 2010 and ISCO-08, the international standard used as the bridge to UK classifications.</p>

		<h3>Step 4 &ndash; ISCO-08 &rarr; UK SOC 2020</h3>
		<p>The ONS SOC 2020 coding index includes ISCO-08 codes for each entry. We extract unique ISCO-08 &rarr; UK SOC 2020 pairs from this index.</p>

		<h3>Weighting scheme</h3>
		<p>Each O*NET occupation may map to multiple UK SOC codes. The contribution weight is uniform: if an O*NET code maps to N distinct UK SOC codes, each receives weight 1/N. This ensures every O*NET occupation's total contribution sums to 1.0 across all UK SOC codes it feeds into.</p>
		<p>The result is a crosswalk table with columns: <code>onet_soc</code>, <code>onet_title</code>, <code>uk_soc_2020</code>, <code>uk_soc_title</code>, <code>weight</code>.</p>
	</div>

	<div class="card">
		<h2>3. Data translation</h2>
		<p>Each UK SOC 2020 unit group becomes a "superposition" of its contributing US O*NET occupations. The translation method depends on data type:</p>

		<h3>Rated (continuous) data</h3>
		<p>For data with numeric scores &ndash; abilities, skills, knowledge, work activities, work context, work styles, interests, work values &ndash; we compute <strong>weighted averages</strong>:</p>
		<pre><code>UK_value(element, scale) = &Sigma; (weight_i &times; ONET_value_i) / &Sigma; weight_i</code></pre>
		<p>where the sum is over all contributing O*NET occupations. This produces smooth, reasonable values even when many sources contribute. For example, a UK programming occupation that draws from 15 O*NET software roles will have its "Programming" skill score dominated by the high-scoring sources.</p>
		<p>Education and job zone data are also averaged using the same weighted scheme.</p>

		<h3>Discrete (categorical/text) data</h3>
		<p>For data that cannot be meaningfully averaged &ndash; tasks, technology skills, tools used, detailed work activities, emerging tasks, reported job titles, alternate titles &ndash; we <strong>collect all unique items</strong> from all contributing O*NET occupations. Items are sorted by their contribution weight (sum of source weights).</p>
		<p>This is where the many-to-one mapping introduces noise: a UK occupation inherits <em>everything</em> from all its source occupations. For example, UK SOC 5313 (Bricklayers) maps from 10 US occupations including Hazardous Materials Removal Workers, Solar Photovoltaic Installers, and Weatherization Installers, inheriting their technology skills and task statements even when they are clearly irrelevant to bricklaying.</p>

		<h3>Related occupations</h3>
		<p>Related occupations from O*NET are re-mapped through the crosswalk to produce UK SOC-to-UK SOC relationships. Self-references (where a related occupation maps to the same UK SOC code) are removed.</p>
	</div>

	<div class="card">
		<h2>4. LLM refinement</h2>
		<p>To address the crosswalk noise in discrete data, an optional LLM refinement step filters and deduplicates technology skills and tasks.</p>

		<h3>What gets refined</h3>
		<div class="table-wrap">
			<table>
				<thead>
					<tr><th>Category</th><th>Operation</th><th>Rationale</th></tr>
				</thead>
				<tbody>
					<tr><td>Technology skills</td><td>Filter irrelevant items</td><td>Crosswalk noise is most visible here (e.g. Jenkins CI, Salesforce for Bricklayers)</td></tr>
					<tr><td>Tools used</td><td>Filter irrelevant items</td><td>Same crosswalk noise as technology skills &ndash; physical tools from unrelated source occupations</td></tr>
					<tr><td>Tasks</td><td>Deduplicate + filter irrelevant</td><td>Multiple O*NET sources contribute overlapping or unrelated task statements</td></tr>
				</tbody>
			</table>
		</div>
		<p><strong>Rated data is NOT refined.</strong> Weighted averaging already handles crosswalk noise smoothly for continuous numeric scores &ndash; the irrelevant sources are naturally diluted by the relevant ones.</p>

		<h3>Conservative philosophy</h3>
		<p>The LLM is instructed to be <strong>conservative</strong>: only remove items that are <em>clearly</em> irrelevant. Generic tools (Microsoft Office, email, web browsers) are kept for almost all occupations. When in doubt, items are preserved. This prevents the LLM from over-filtering legitimate but uncommon technology associations.</p>

		<h3>Technology skill and tools used filtering</h3>
		<p>The LLM receives the occupation title, description, source US occupations, and a numbered list of technology skills (or tools/equipment). It returns a verdict (relevant/irrelevant) for each item. Items with no verdict are kept (fail-safe conservative default). The same approach is used for both technology skills (software) and tools used (physical equipment).</p>

		<h3>Task refinement</h3>
		<p>The LLM receives task statements (with Core/Supplemental/Unclassified type labels) and is asked to:</p>
		<ol>
			<li><strong>Deduplicate near-identical tasks</strong> by grouping them and selecting the best original phrasing</li>
			<li><strong>Remove clearly irrelevant tasks</strong> that do not belong to this occupation</li>
		</ol>
		<p>No LLM-generated text appears in the final dataset &ndash; the model only selects among and filters original O*NET task statements. Every original task must appear exactly once: as a selected representative, in a duplicate group, or in the removal list.</p>

		<h3>Chunking and deduplication</h3>
		<p>For occupations with very large item lists (&gt;400 tech skills or &gt;150 tasks), input is split into chunks processed independently. After task chunking, a deterministic post-processing pass merges any cross-chunk duplicates using Jaccard word-overlap (threshold: 0.85).</p>

		<h3>Models</h3>
		<p>Each refinement task uses an independently configurable model. Technology and tool filtering (simple relevance judgements) use <code>gpt-5-mini</code>. Task deduplication and filtering, which requires semantic similarity understanding, also uses <code>gpt-5-mini</code> by default but can be upgraded to a stronger model if needed. At ~2,860 API calls across 410 occupations, a full run costs under $5. All responses are cached, so re-runs are free.</p>
	</div>

	<div class="card">
		<h2>5. Output format</h2>
		<p>The pipeline produces per-occupation JSON files, plus an occupation index and crosswalk file.</p>

		<h3>Data categories</h3>
		<div class="table-wrap">
			<table>
				<thead>
					<tr><th>Category</th><th>Type</th><th>Scales</th><th>Description</th></tr>
				</thead>
				<tbody>
					<tr><td>Abilities</td><td>Rated</td><td>IM (importance), LV (level)</td><td>Enduring attributes relevant to work performance</td></tr>
					<tr><td>Skills</td><td>Rated</td><td>IM, LV</td><td>Developed capacities for performing work activities</td></tr>
					<tr><td>Knowledge</td><td>Rated</td><td>IM, LV</td><td>Sets of principles and facts relevant to work</td></tr>
					<tr><td>Work Activities</td><td>Rated</td><td>IM, LV</td><td>General types of job behaviours</td></tr>
					<tr><td>Work Context</td><td>Rated</td><td>Various</td><td>Physical and social factors of the work environment</td></tr>
					<tr><td>Work Styles</td><td>Rated</td><td>IM</td><td>Personal characteristics for job performance</td></tr>
					<tr><td>Interests</td><td>Rated</td><td>OI (occupational interest)</td><td>Holland/RIASEC interest profiles</td></tr>
					<tr><td>Work Values</td><td>Rated</td><td>EX (extent)</td><td>Work aspects valued by workers</td></tr>
					<tr><td>Tasks</td><td>Discrete</td><td>relevance, importance</td><td>Specific work activities performed</td></tr>
					<tr><td>Technology Skills</td><td>Discrete</td><td>weight</td><td>Software and technologies used</td></tr>
					<tr><td>Tools Used</td><td>Discrete</td><td>weight</td><td>Physical tools and equipment used</td></tr>
					<tr><td>Detailed Work Activities</td><td>Discrete</td><td>weight</td><td>Fine-grained activity statements</td></tr>
					<tr><td>Emerging Tasks</td><td>Discrete</td><td>&ndash;</td><td>Newly identified or revised task statements</td></tr>
					<tr><td>Education</td><td>Rated</td><td>&ndash;</td><td>Education, training, and experience requirements</td></tr>
					<tr><td>Job Zone</td><td>Numeric</td><td>1&ndash;5</td><td>Preparation level (1=little, 5=extensive)</td></tr>
				</tbody>
			</table>
		</div>
	</div>

	<div class="card">
		<h2>6. Limitations</h2>
		<ul class="limitations">
			<li><strong>Crosswalk chain noise.</strong> The four-step crosswalk introduces many-to-many mappings. Some UK SOC codes inherit data from tangentially related US occupations. LLM refinement mitigates the worst of this for discrete data, but the underlying crosswalk is imperfect.</li>
			<li><strong>US-source bias.</strong> All data originates from the US O*NET programme. Occupation structures, skill requirements, and technology usage may differ in the UK labour market. The pipeline translates occupation <em>classifications</em> but cannot adapt the underlying occupational data to UK-specific realities.</li>
			<li><strong>ISCO-08 as bridge.</strong> ISCO-08 is coarser than both US SOC and UK SOC, so the bridge step necessarily groups occupations that may be distinct in either national system.</li>
			<li><strong>LLM judgement boundaries.</strong> The refinement step relies on an LLM's assessment of item relevance. While conservative prompting reduces false removals, the model may occasionally keep irrelevant items or remove marginally relevant ones.</li>
			<li><strong>Uniform weighting.</strong> All contributing O*NET codes receive equal weight (1/N). A more sophisticated approach might weight by occupational similarity, but no suitable similarity metric exists across classification systems.</li>
		</ul>
	</div>

	<div class="card">
		<h2>7. Reproducibility</h2>
		<ul class="limitations">
			<li><strong>Caching.</strong> All LLM API calls are cached to disk. Once a response is cached, re-running the pipeline produces identical output at zero API cost.</li>
			<li><strong>Deterministic thresholds.</strong> The Jaccard deduplication threshold (0.85) is fixed and applied deterministically after LLM processing.</li>
			<li><strong>Data versioning.</strong> The pipeline is pinned to O*NET v30.2 and the March 2025 edition of the ONS SOC 2020 coding index.</li>
		</ul>
	</div>
</div>

<style>
	.intro {
		font-size: 1rem;
		line-height: 1.7;
	}

	.card p {
		font-size: 0.9375rem;
		line-height: 1.7;
		color: var(--color-text);
		margin-bottom: 0.75rem;
	}

	.card p:last-child {
		margin-bottom: 0;
	}

	h2 {
		font-size: 1.2rem;
		margin-bottom: 0.75rem;
	}

	h3 {
		font-size: 0.95rem;
		font-weight: 600;
		color: var(--color-primary);
		margin: 1.25rem 0 0.4rem;
	}

	.crosswalk-chain {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
		padding: 1rem;
		background: var(--color-bg);
		border-radius: var(--radius);
		margin: 0.75rem 0;
	}

	.chain-step {
		padding: 0.35rem 0.75rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		font-size: 0.8125rem;
		font-weight: 600;
		white-space: nowrap;
	}

	.chain-arrow {
		color: var(--color-text-secondary);
		font-size: 1rem;
	}

	.table-wrap {
		overflow-x: auto;
		margin: 0.75rem 0;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.8125rem;
	}

	th, td {
		text-align: left;
		padding: 0.5rem 0.75rem;
		border-bottom: 1px solid var(--color-border);
	}

	th {
		font-weight: 600;
		background: var(--color-bg);
		white-space: nowrap;
	}

	pre {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		padding: 0.75rem 1rem;
		overflow-x: auto;
		margin: 0.75rem 0;
	}

	code {
		font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
		font-size: 0.8125rem;
	}

	ol {
		padding-left: 1.25rem;
		margin: 0.5rem 0;
	}

	ol li {
		font-size: 0.9375rem;
		line-height: 1.7;
		margin-bottom: 0.25rem;
	}

	.limitations {
		padding-left: 1.25rem;
		margin-top: 0.25rem;
	}

	.limitations li {
		font-size: 0.9375rem;
		line-height: 1.7;
		margin-bottom: 0.5rem;
	}
</style>
