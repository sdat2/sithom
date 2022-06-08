# Tests

Tests are an important way of improving code reliability.

<https://braaannigan.github.io/software/2022/06/06/testing-for-data-science-intro.html>

Ideally code should repeat itself as scarely as possible.

Therefore examples in docstrings should ideally run as tests as well.

To do this we could use:

- <https://docs.python.org/3/library/doctest.html>, 
- or `pytest --doctest-modules` <https://docs.pytest.org/en/6.2.x/doctest.html>,
