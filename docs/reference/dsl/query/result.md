Module superlinked.framework.dsl.query.result
=============================================

Classes
-------

`Result(entries: Sequence[superlinked.framework.dsl.query.result.ResultEntry], query_descriptor: superlinked.framework.dsl.query.query_descriptor.QueryDescriptor, search_vector: superlinked.framework.common.data_types.Vector)`
:   Represents the outcome of a query operation.
    Attributes:
        entries (Sequence[ResultEntry]): A sequence of result entries, each encapsulating an entity and its data.
        query_descriptor (QueryDescriptor): The descriptor detailing the query's parameters and structure.
        search_vector (Vector): The vector used in the search operation.

    ### Class variables

    `entries: Sequence[superlinked.framework.dsl.query.result.ResultEntry]`
    :

    `query_descriptor: superlinked.framework.dsl.query.query_descriptor.QueryDescriptor`
    :

    `search_vector: superlinked.framework.common.data_types.Vector`
    :

    ### Instance variables

    `entities: list[superlinked.framework.common.storage_manager.search_result_item.SearchResultItem]`
    :

    `knn_params: dict[str, typing.Any]`
    :

    `schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject`
    :

    ### Methods

    `to_pandas(self) ‑> pandas.core.frame.DataFrame`
    :   Converts the query result entries into a pandas DataFrame.
        
        Each row in the DataFrame corresponds to a single entity in the result, with
        columns representing the fields of the stored objects. An additional score column
        is present which shows similarity to the query vector.
        
        Returns:
            DataFrame: A pandas DataFrame where each row represents a result entity, and
                each column corresponds to the fields of the stored objects. Additionally,
                it contains the above-mentioned score column.
            ValueError: If both 'similarity_score' and 'superlinked_similarity_score' fields are present.

`ResultEntry(entity: superlinked.framework.common.storage_manager.search_result_item.SearchResultItem, stored_object: dict[str, typing.Any])`
:   Represents a single entry in a Result, encapsulating the entity and its associated data.
    
    Attributes:
        entity (SearchResultItem): The entity of the result entry.
            This is an instance of the SearchResultItem class, which represents a unique entity in the system.
            It contains header information such as the entity's ID and schema and the queried fields.
        stored_object (dict[str, Any]): The stored object of the result entry.
            This is essentially the raw data that was input into the system.

    ### Class variables

    `entity: superlinked.framework.common.storage_manager.search_result_item.SearchResultItem`
    :

    `stored_object: dict[str, typing.Any]`
    :