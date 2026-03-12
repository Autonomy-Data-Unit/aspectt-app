<svelte:head><title>About - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">About ASPECTT</h1>

	<div class="card">
		<h2>What is ASPECTT?</h2>
		<p>
			ASPECTT is a multidimensional occupational database for the UK. It covers the skills,
			tasks, abilities, knowledge, technologies and work characteristics of 412 UK occupations,
			classified under SOC 2020.
		</p>
		<p>
			The UK has no direct equivalent of the US O*NET system, which gives detailed
			occupational data to researchers, policymakers, careers advisers and employers.
			ASPECTT fills that gap by adapting O*NET data for a UK context using a series
			of standard occupation code crosswalks.
		</p>
	</div>

	<div class="card" id="use-cases">
		<h2>Using ASPECTT</h2>
		<div class="use-case-grid">
			<div class="use-case">
				<h3>National or local government</h3>
				<p>ASPECTT will help design fair and efficient transition plans for workforces, as we make the shift from carbon-intensive industries to sustainable sectors. By giving a high-resolution image of the possible pipelines between jobs, policymakers can move from speculation to action-planning. ASPECTT can also give insight into the changing trajectory of skills, tasks and abilities in the labour market over time.</p>
			</div>
			<div class="use-case">
				<h3>Trade unions</h3>
				<p>ASPECTT will help trade unions plan for the future for their members. By unpacking the occupational elements of a sector, ASPECTT allows trade unions to see the value of certain skills/expertise and the possible avenues for role adaptions in light of the changing nature of our economy and climate. ASPECTT also allows for forecasting the threat of automation with regards to certain tasks on the job, so trade unions can craft policy and campaigns accordingly.</p>
			</div>
			<div class="use-case">
				<h3>NGOs and campaign groups</h3>
				<p>ASPECTT will give you the highest resolution image of what a just or green transition could look like at the level of jobs and industries. With this knowledge, your campaigns and your reports will be best equipped to confront the obstacles to change as we strive to move towards a sustainable economic model.</p>
			</div>
			<div class="use-case">
				<h3>Business leaders</h3>
				<p>ASPECTT will help you understand the task, skill, expertise and educational composition of your workforce and the sector you are in. It will help plot possible avenues for transition away from unsustainable working practices and towards sustainable job roles for your enterprise.</p>
			</div>
			<div class="use-case">
				<h3>Universities</h3>
				<p>ASPECTT will help you understand the skills composition of the UK labour market currently and over the past few decades. Its high-resolution data will show the wage value of certain skills and educational qualifications, allowing for the more precise planning of courses and modules. Which abilities and skills are scarce in the labour market today? Which skills and abilities receive the highest remuneration and which undergraduate and graduate courses might best fit these occupations?</p>
			</div>
			<div class="use-case">
				<h3>Academics and researchers</h3>
				<p>ASPECTT will contribute greatly to studies across a number of disciplines. If you work in economics, sociology, public policy, environmental studies, climate science and others, ASPECTT will be able to augment your research questions with robust, detailed data on occupational characteristics unavailable elsewhere. Tailoring the database to your research questions, Autonomy can act as an industry partner as part of your research project to deliver results.</p>
			</div>
		</div>
	</div>

	<div class="card">
		<h2>Methodology</h2>
		<p class="subtitle"><a href="/methodology">Full technical methodology &rarr;</a></p>
		<p>
			ASPECTT maps US O*NET occupations to UK SOC 2020 codes through a chain of crosswalks:
		</p>
		<div class="crosswalk-chain">
			<span class="chain-step">US O*NET SOC</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">US SOC 2018</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">US SOC 2010</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">ISCO-08</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">UK SOC 2020</span>
		</div>
		<p>
			Where a UK occupation maps to more than one US O*NET occupation, the data is combined
			using uniform weights. Each UK occupation therefore represents a weighted average of its
			contributing O*NET sources. The mappings and weights are visible on the
			<a href="/crosswalk">crosswalk page</a> and in the 'Sources' tab of each occupation.
		</p>
		<p>
			The O*NET data comes from version 30.2 of the O*NET database. The ISCO-08 to SOC
			crosswalk is provided by the US Bureau of Labor Statistics, and the UK SOC 2020 coding
			index is published by the Office for National Statistics.
		</p>
		<p>
			For full technical details including the LLM refinement step, weighting scheme, and data format,
			see the <a href="/methodology">detailed methodology</a>.
		</p>
	</div>

	<div class="card">
		<h2>Data categories</h2>
		<p>Each occupation in ASPECTT includes information across these categories:</p>
		<ul class="data-list">
			<li><strong>Tasks</strong> &ndash; specific work activities carried out in the occupation</li>
			<li><strong>Skills</strong> &ndash; developed capacities that facilitate learning or performance</li>
			<li><strong>Abilities</strong> &ndash; enduring attributes that influence performance</li>
			<li><strong>Knowledge</strong> &ndash; organised sets of principles and facts</li>
			<li><strong>Technology skills</strong> &ndash; software, tools and technologies used</li>
			<li><strong>Work activities</strong> &ndash; general types of job behaviour</li>
			<li><strong>Work context</strong> &ndash; physical and social conditions of work</li>
			<li><strong>Work styles</strong> &ndash; personal characteristics relevant to performance</li>
			<li><strong>Interests</strong> &ndash; Holland (RIASEC) interest profiles</li>
			<li><strong>Work values</strong> &ndash; what workers in the occupation tend to value</li>
			<li><strong>Education</strong> &ndash; typical preparation level required</li>
		</ul>
	</div>

	<div class="card">
		<h2>Who built this</h2>
		<p>
			ASPECTT is produced by the <a href="https://autonomy.work/adu/" target="_blank" rel="noopener">Autonomy Data Unit</a>,
			the research and analytics division of the
			<a href="https://autonomy.work/" target="_blank" rel="noopener">Autonomy Institute</a>.
			Autonomy is an independent research organisation that creates data-driven tools and
			policy to strengthen democracy and build the future economy. Its work spans labour
			markets, public services and digital infrastructure.
		</p>
		<p>
			The Data Unit combines datasets, builds research tools and develops data visualisations
			to support policy research. ASPECTT gives UK researchers and policymakers access to the
			kind of granular occupational data that O*NET provides in the US.
		</p>
	</div>

	<div class="card">
		<h2>Further reading</h2>
		<ul class="link-list">
			<li><a href="https://autonomy.work/wp-content/uploads/2022/01/Aspectt-occupational-tool.pdf" target="_blank" rel="noopener">ASPECTT brochure (PDF)</a></li>
			<li><a href="https://github.com/Autonomy-Data-Unit/aspectt-app" target="_blank" rel="noopener">Source code on GitHub</a></li>
			<li><a href="https://autonomy.work/adu/" target="_blank" rel="noopener">Autonomy Data Unit</a></li>
			<li><a href="https://autonomy.work/" target="_blank" rel="noopener">Autonomy Institute</a></li>
			<li><a href="/api">ASPECTT public API</a></li>
		</ul>
	</div>

	<div class="card" id="contact">
		<h2>Contact</h2>
		<p>
			For general inquiries about ASPECTT, or if you are interested in commissioning
			bespoke occupational analysis using the ASPECTT data, please get in touch at
			<a href="mailto:aspectt@autonomy.work">aspectt@autonomy.work</a>.
		</p>
	</div>
</div>

<style>
	.card p {
		font-size: 0.9375rem;
		line-height: 1.7;
		color: var(--color-text);
		margin-bottom: 0.75rem;
	}

	.card p:last-child {
		margin-bottom: 0;
	}

	.subtitle {
		font-size: 0.8125rem;
		margin-top: -0.25rem;
		margin-bottom: 1rem;
	}

	.subtitle a {
		color: var(--color-accent);
		font-weight: 500;
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

	.data-list {
		padding-left: 1.25rem;
		margin-top: 0.5rem;
	}

	.data-list li {
		font-size: 0.875rem;
		line-height: 1.6;
		margin-bottom: 0.25rem;
	}

	.link-list {
		padding-left: 1.25rem;
	}

	.link-list li {
		font-size: 0.875rem;
		line-height: 1.8;
	}

	.use-case-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1.25rem;
		margin-top: 0.75rem;
	}

	.use-case h3 {
		font-size: 0.9rem;
		font-weight: 600;
		margin-bottom: 0.375rem;
		color: var(--color-primary);
	}

	.use-case p {
		font-size: 0.8125rem;
		line-height: 1.6;
	}

	@media (max-width: 900px) {
		.use-case-grid { grid-template-columns: repeat(2, 1fr); }
	}

	@media (max-width: 600px) {
		.use-case-grid { grid-template-columns: 1fr; }
	}
</style>
