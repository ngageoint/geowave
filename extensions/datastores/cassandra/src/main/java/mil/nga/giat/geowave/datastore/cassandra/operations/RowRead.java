package mil.nga.giat.geowave.datastore.cassandra.operations;

import java.io.IOException;
import java.nio.ByteBuffer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.datastax.driver.core.BoundStatement;
import com.datastax.driver.core.PreparedStatement;
import com.datastax.driver.core.Statement;

import mil.nga.giat.geowave.core.store.CloseableIterator;
import mil.nga.giat.geowave.core.store.entities.GeoWaveRow;
import mil.nga.giat.geowave.datastore.cassandra.CassandraDataStore;
import mil.nga.giat.geowave.datastore.cassandra.CassandraRow;
import mil.nga.giat.geowave.datastore.cassandra.CassandraRow.CassandraField;

public class RowRead
{
	private final static Logger LOGGER = LoggerFactory.getLogger(RowRead.class);
	private final CassandraOperations operations;
	private final PreparedStatement preparedRead;
	private byte[] adapterId;
	private byte[] partitionKey;
	private byte[] sortKey;

	protected RowRead(
			final PreparedStatement preparedRead,
			final CassandraOperations operations ) {
		this(
				preparedRead,
				operations,
				null,
				null,
				null);
	}

	protected RowRead(
			final PreparedStatement preparedRead,
			final CassandraOperations operations,
			final byte[] partitionKey,
			final byte[] sortKey,
			final byte[] adapterId ) {
		this.preparedRead = preparedRead;
		this.operations = operations;
		this.partitionKey = partitionKey;
		this.sortKey = sortKey;
		this.adapterId = adapterId;
	}

	public GeoWaveRow result() {
		if (partitionKey != null && sortKey != null) {
			final BoundStatement boundRead = new BoundStatement(
					preparedRead);
			boundRead.set(
					CassandraField.GW_SORT_KEY.getBindMarkerName(),
					ByteBuffer.wrap(sortKey),
					ByteBuffer.class);
			boundRead.set(
					CassandraField.GW_ADAPTER_ID_KEY.getBindMarkerName(),
					ByteBuffer.wrap(adapterId),
					ByteBuffer.class);
			boundRead.set(
					CassandraField.GW_PARTITION_ID_KEY.getBindMarkerName(),
					ByteBuffer.wrap(partitionKey),
					ByteBuffer.class);
			try (CloseableIterator<GeoWaveRow> it = operations.executeQuery(boundRead)) {
				if (it.hasNext()) {
					// there should only be one entry with this index
					return it.next();
				}
			}
			catch (final IOException e) {
				LOGGER.warn(
						"Unable to close cassandra query",
						e);
			}
		}
		return null;
	}
}
