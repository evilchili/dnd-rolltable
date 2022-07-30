    Generate a roll table using weighted distributions of random options.
    Given source.yaml containing options such as:

        option1:
            - key1: description
            - key2: description
            ...
        ...

    Generate a random table:

        >>> print(RollTable(path='source.yaml'))
        d1    option6    key3   description
        d2    option2    key2   description
        d3    option3    key4   description
        ...

    You can customize the frequency distribution, headers, and table size by
    defining metadata in your source file.

    Using Metadata:

    By default options are given uniform distribution and random keys will be
    selected from each option with equal probability. This behaviour can be
    changed by adding an optional metadata section to the source file:

        metadata:
          frequenceis:
            default:
              option1: 0.5
              option2: 0.1
              option3: 0.3
              option4: 0.1

    This will guarantee that random keys from option1 are selected 50% of the
    time, from option 2 10% of the time, and so forth. Frequencies should add
    up to 1.0.

    If the metadata section includes 'frequencies', The 'default' distribution
    must be defined. Additional optional distributions may also be defined, if
    you want to provide alternatives for specific use cases.

        metadata:
          frequenceis:
            default:
              option1: 0.5
              option2: 0.1
              option3: 0.3
              option4: 0.1
            inverted:
              option1: 0.1
              option2: 0.3
              option3: 0.1
              option4: 0.5

    A specific frequency distribution can be specifed by passing the 'frequency'
    parameter at instantiation:

        >>> t = RollTable('source.yaml', frequency='inverted')

    The metadata section can also override the default size of die to use for
    the table (a d20). For example, this creates a 100-row table:

        metadata:
          die: 100

    This too can be overridden at instantiation:

        >>> t = RollTable('source.yaml', die=64)

    Finally, headers for your table columns can also be defined in metadata:

        metadata:
          headers:
              - Roll
              - Frequency
              - Description
              - Effect

     This will yield output similar to:

        >>> print(RollTable(path='source.yaml'))
        Roll  Category   Name   Effect
        d1    option6    key3   description
        d2    option2    key2   description
        d3    option3    key4   description
        ...
 
